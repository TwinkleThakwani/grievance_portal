from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from datetime import timedelta
from flask_cors import CORS
import mysql.connector
from datetime import date
import os
CORS(app)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Load sensitive configuration from environment variables
# Provide safe defaults for local development but do not hardcode secrets
app.secret_key = os.environ.get('SECRET_KEY') or os.environ.get('FLASK_SECRET') or os.urandom(24).hex()

# Enable CORS after app is created
CORS(app)
CORS(app)

# Database configuration

def get_db_connection():
    """Create a MySQL connection using environment variables.

    Supports either a full `DATABASE_URL` (mysql://user:pass@host:port/dbname)
    or individual env vars: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME.
    """
    database_url = os.environ.get('DATABASE_URL')
    connect_kwargs = {}

    if database_url:
        # Parse DATABASE_URL like: mysql://user:pass@host:port/dbname
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            connect_kwargs['host'] = parsed.hostname or 'localhost'
            connect_kwargs['user'] = parsed.username or os.environ.get('DB_USER', 'root')
            connect_kwargs['password'] = parsed.password or os.environ.get('DB_PASSWORD', '')
            # Path starts with '/', strip it
            connect_kwargs['database'] = (parsed.path[1:] if parsed.path and parsed.path.startswith('/') else parsed.path) or os.environ.get('DB_NAME')
            if parsed.port:
                connect_kwargs['port'] = parsed.port
        except Exception:
            # Fallback to individual variables
            connect_kwargs['host'] = os.environ.get('DB_HOST', 'localhost')
            connect_kwargs['user'] = os.environ.get('DB_USER', 'root')
            connect_kwargs['password'] = os.environ.get('DB_PASSWORD', '')
            connect_kwargs['database'] = os.environ.get('DB_NAME', 'college_project')
    else:
        connect_kwargs['host'] = os.environ.get('DB_HOST', 'localhost')
        connect_kwargs['user'] = os.environ.get('DB_USER', 'root')
        connect_kwargs['password'] = os.environ.get('DB_PASSWORD', '')
        connect_kwargs['database'] = os.environ.get('DB_NAME', 'college_project')

    # Optional flags
    connect_kwargs['use_pure'] = True
    ssl_disabled = os.environ.get('DB_SSL_DISABLED', 'True').lower()
    connect_kwargs['ssl_disabled'] = ssl_disabled in ('1', 'true', 'yes')

    return mysql.connector.connect(**connect_kwargs)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    role = data['role']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query the appropriate table based on the role
    if role == 'student':
        cursor.execute("SELECT student_id AS id, name, email FROM students WHERE email = %s AND password = %s", (email, password))
    elif role == 'investigator':
        cursor.execute("SELECT investigator_id AS id, name, email FROM investigators WHERE email = %s AND password = %s", (email, password))
    elif role == 'admin':
        cursor.execute("SELECT admin_id AS id, name, email FROM admins WHERE email = %s AND password = %s", (email, password))
    else:
        return jsonify({'error': 'Invalid role'}), 400

    user = cursor.fetchone()
    conn.close()

    if user:
        # Store user details in the session
        session['id'] = user['id']  # Use normalized 'id' regardless of role
        session['role'] = role
        session['name'] = user['name']
        session['email'] = user['email']
        return jsonify({'message': 'Login successful', 'role': role})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
@app.route('/anti_ragging')
def anti_ragging():
    return render_template('anti_ragging.html')

@app.route('/grievance_committee')
def grievance_committee():
    return render_template('grievance_committee.html')
@app.route('/logout.html')
def logout():
    # Clear the session
    session.clear()
    # Render the logout page
    return render_template('logout.html')
@app.route('/register.html')
def register():
    return render_template('register.html')
@app.route('/register', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the new user into the appropriate table based on the role
    if role == 'student':
        cursor.execute('''
            INSERT INTO students (name, email, password)
            VALUES (%s, %s, %s)
        ''', (name, email, password))
    elif role == 'investigator':
        cursor.execute('''
            INSERT INTO investigators (name, email, password)
            VALUES (%s, %s, %s)
        ''', (name, email, password))
    elif role == 'admin':
        cursor.execute('''
            INSERT INTO admins (name, email, password)
            VALUES (%s, %s, %s)
        ''', (name, email, password))

    conn.commit()
    conn.close()

    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('index'))
@app.route('/forgot_password.html')
def forgot_password():
    return render_template('about_us.html')
@app.route('/about_us.html')
def about_us():
    return render_template('about_us.html')
@app.route('/contact_us.html')
def contact_us():
    return render_template('contact_us.html')
@app.route('/privacy_policy.html')
def privacy_policy():
    return render_template('privacy_policy.html')
@app.route('/case_history.html')
def case_history():
    return render_template('case_history.html')

@app.route('/counseling.html')
def counseling():
    return render_template('counseling.html')
@app.route('/student_dashboard.html')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/admin_dashboard.html')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/investigator_dashboard.html')
def investigator_dashboard():
    return render_template('investigator_dashboard.html')

@app.route('/student_form.html')
def student_form():
    return render_template('student_form.html')

@app.route('/view_complaints.html')
def view_complaints():
    if 'id' not in session or 'role' not in session:
        # Redirect to login if the user is not logged in
        return redirect(url_for('index'))
    
    user_id = session['id']  # Get the logged-in user's ID
    role = session['role']  # Get the logged-in user's role
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query complaints based on the user's role
    if role == 'student':
        cursor.execute('''
            SELECT g.grievance_id, g.description, s.student_id AS reg_no, g.type_of_grievance, 
                   g.respondent, g.witness, g.incident_time, g.incident_location
            FROM grievances g
            JOIN students s ON g.student_id = s.student_id
            WHERE s.student_id = %s
        ''', (user_id,))
    elif role == 'investigator':
        cursor.execute('''
            SELECT g.grievance_id, g.description, s.student_id AS reg_no, g.type_of_grievance, 
                   g.respondent, g.evidence AS witness, g.incident_time, g.incident_location
            FROM grievances g
            JOIN grievance_assignments ga ON g.grievance_id = ga.grievance_id
            JOIN students s ON g.student_id = s.student_id
            WHERE ga.investigator_id = %s
        ''', (user_id,))
    elif role == 'admin':
        # Admins can view all complaints
        cursor.execute('''
            SELECT g.grievance_id, g.description, s.student_id AS reg_no, g.type_of_grievance, 
                   g.respondent, g.incident_time, g.incident_location
            FROM grievances g
            JOIN students s ON g.student_id = s.student_id
        ''')
    else:
        conn.close()
        return redirect(url_for('index'))
    
    complaints = cursor.fetchall()
    conn.close()
    return render_template('view_complaints.html', complaints=complaints)


@app.route('/feedback.html')
def feedback():
    if 'id' not in session or 'role' not in session:
        # Redirect to login if the user is not logged in
        flash('You must be logged in to view feedback.', 'error')
        return redirect(url_for('index'))

    user_id = session['id']  # Get the logged-in student's ID
    role = session['role']  # Get the logged-in user's role

    if role != 'student':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch grievances submitted by the logged-in student
        cursor.execute('''
            SELECT grievance_id,description
            FROM grievances
            WHERE student_id = %s
            
        ''', (user_id,))
        grievances = cursor.fetchall()

        # Fetch the student's name for the form
        cursor.execute('''
            SELECT name 
            FROM students 
            WHERE student_id = %s
        ''', (user_id,))
        student = cursor.fetchone()

        conn.close()
        return render_template('feedback.html', grievances=grievances, student=student)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error fetching feedback data.', 'error')
        return redirect(url_for('index'))


# ... existing code ...

@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if 'id' not in session or 'role' not in session:
        # Redirect to login if the user is not logged in
        flash('You must be logged in to submit a complaint.', 'error')
        return redirect(url_for('index'))

    user_id = session['id']  # Get the logged-in student's ID
    role = session['role']  # Get the logged-in user's role

    if role != 'student':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get form data
        incident_location = request.form.get('incident_location')
        incident_date = request.form.get('incident_date')
        incident_time = request.form.get('incident_time')
        description = request.form.get('description')
        respondent = request.form.get('respondent')
        type_of_grievance = request.form.get('type_of_grievance')
        witness = request.form.get('witness')  # Handle file upload

        # Save evidence file if uploaded

        # Insert the complaint into the grievances table
        cursor.execute('''
            INSERT INTO grievances (
                student_id, 
                incident_location, 
                incident_date, 
                incident_time, 
                description, 
                respondent, 
                type_of_grievance, 
                witness
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            user_id,
            incident_location,
            incident_date,
            incident_time,
            description,
            respondent,
            type_of_grievance,
            witness
        ))

        conn.commit()
        flash('Your complaint has been submitted successfully!', 'success')
        return redirect(url_for('form_submit'))

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        conn.rollback()
        flash('An error occurred while submitting the complaint. Please try again.', 'error')
        return redirect(url_for('student_form'))

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'id' not in session or 'role' not in session:
        flash('You must be logged in to submit feedback.', 'error')
        return redirect(url_for('index'))

    student_id = session['id']  # Get the logged-in student's ID

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (grievance_id, student_id, rating, comments, submitted_at)
        VALUES (%s, %s, %s, %s, NOW())
    ''', (
        request.form['grievance_id'],
        student_id,
        request.form['rating'],
        request.form['comments']
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('form_submit'))
@app.route('/assign_investigators.html')
def assign_investigators():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch grievances with their assigned investigator details, including grievances with no assignments
        cursor.execute('''
            SELECT g.grievance_id, g.description, g.type_of_grievance, g.incident_date, g.incident_location,
                   ga.investigator_id AS assigned_investigator_id,
                   i.name AS investigator_name, i.active AS investigator_active,
                   ga.assigned_at
            FROM grievances g
            LEFT JOIN grievance_assignments ga 
                ON g.grievance_id = ga.grievance_id
            LEFT JOIN investigators i 
                ON ga.investigator_id = i.investigator_id
            WHERE ga.assigned_at IS NULL OR ga.assigned_at = (
                SELECT MAX(ga2.assigned_at)
                FROM grievance_assignments ga2
                WHERE ga2.grievance_id = g.grievance_id
            )
        ''')
        grievances = cursor.fetchall()

        # Fetch only active investigators for the dropdown
        cursor.execute('''
            SELECT investigator_id, name, email, department
            FROM investigators
            WHERE active = 1
            ORDER BY name
        ''')
        investigators = cursor.fetchall()

        conn.close()
        return render_template('assign_investigators.html', grievances=grievances, investigators=investigators)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error fetching data for assigning investigators.', 'error')
        return redirect(url_for('admin_dashboard'))
@app.route('/assign_investigator', methods=['POST'])
def assign_investigator():
    grievance_id = request.form.get('grievance_id')
    investigator_id = request.form.get('investigator_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert a new record for the assignment, even if the same investigator is reassigned
        cursor.execute('''
            INSERT INTO grievance_assignments (grievance_id, investigator_id, assigned_at)
            VALUES (%s, %s, NOW())
        ''', (grievance_id, investigator_id))

        conn.commit()
        conn.close()

        # Redirect with a success message in the query parameters
        return redirect(url_for('assign_investigators', message='Investigator assigned/reassigned successfully!'))

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database Error: {err}")
        flash('Error assigning/reassigning investigator. Please try again.', 'error')

    finally:
        conn.close()

    return redirect(url_for('assign_investigators'))

@app.route('/view.html')
def view():
    student_id = 1  # Replace with actual student_id from session or request
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT g.grievance_id, g.department, g.incident_date, i.status, i.priority, i.verdict
        FROM grievances g
        LEFT JOIN investigations i ON g.grievance_id = i.grievance_id
        WHERE g.student_id = %s
    ''', (student_id,))
    grievances = cursor.fetchall()
    conn.close()
    return render_template('view.html', grievances=grievances)
@app.route('/investigator_performance.html')
def investigator_performance():
    return render_template('investigator_performance.html')
@app.route('/assigned.html')
def assigned():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
     
            SELECT 
    i.investigator_id, 
    i.name AS investigator_name, 
    g.grievance_id, 
    g.student_id, 
    g.incident_location, 
    g.incident_date, 
    g.incident_time, 
    g.description, 
    g.respondent, 
    g.witness,
    g.type_of_grievance, 
    inv.status, 
    inv.priority, 
    inv.verdict, 
    inv.enquiry
FROM 
    grievances g
JOIN 
    grievance_assignments ga 
    ON g.grievance_id = ga.grievance_id
JOIN 
    investigators i 
    ON ga.investigator_id = i.investigator_id
JOIN 
    investigations inv 
    ON g.grievance_id = inv.grievance_id
WHERE 
    ga.assigned_at = (
        SELECT MAX(ga2.assigned_at)
        FROM grievance_assignments ga2
        WHERE ga2.grievance_id = g.grievance_id
    )""")
    assigned_records = cursor.fetchall()
    conn.close()
    return render_template('assigned.html', assigned_records=assigned_records)


@app.route('/priority_selector.html')
def priority_selector():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT grievance_id, description FROM grievances')
    grievances = cursor.fetchall()
    conn.close()
    return render_template('priority_selector.html', grievances=grievances)

@app.route('/update_priority', methods=['POST'])
def update_priority():
    grievance_id = request.form['grievance_id']
    priority = request.form['priority']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE investigations SET priority = %s WHERE grievance_id = %s', (priority, grievance_id))
    conn.commit()
    conn.close()
    message = 'Priority updated successfully!'
    return redirect(url_for('priority_selector', message=message))

@app.route('/view_assigned_complaints.html', methods=['GET'])
def view_assigned_complaints():
    type_of_grievance = request.args.get('type_of_grievance', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')

    query = '''
        SELECT g.grievance_id, g.student_id, g.incident_location, g.incident_date, g.incident_time,
               g.description, g.respondent, g.type_of_grievance, g.witness, inv.status, g.priority
        FROM grievances g
        JOIN grievance_assignments ga ON g.grievance_id = ga.grievance_id
        LEFT JOIN investigations inv ON g.grievance_id = inv.grievance_id
        WHERE ga.investigator_id = %s
          AND ga.assigned_at = (
              SELECT MAX(ga2.assigned_at)
              FROM grievance_assignments ga2
              WHERE ga2.grievance_id = g.grievance_id
          )'''
    filters = [session['id']]

    if type_of_grievance:
        query += ' AND g.type_of_grievance = %s'
        filters.append(type_of_grievance)
    if status:
        query += ' AND g.status = %s'
        filters.append(status)
    if priority:
        query += ' AND g.priority = %s'
        filters.append(priority)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, filters)
    complaints = cursor.fetchall()
    conn.close()

    return render_template('view_assigned_complaints.html', complaints=complaints)


@app.route('/status_selector.html')
def status_selector():
    if 'id' not in session or 'role' not in session:
        flash('You must be logged in to access this page.', 'error')
        return redirect(url_for('index'))

    user_id = session['id']  # Get the logged-in investigator's ID
    role = session['role']  # Get the logged-in user's role

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
            SELECT g.grievance_id, g.description
            FROM grievances g
            JOIN grievance_assignments ga ON g.grievance_id = ga.grievance_id
            WHERE ga.investigator_id = %s
              AND ga.assigned_at = (
                  SELECT MAX(ga2.assigned_at)
                  FROM grievance_assignments ga2
                  WHERE ga2.grievance_id = g.grievance_id
              )
        ''', (user_id,))
    
    grievances = cursor.fetchall()
    conn.close()
    return render_template('status_selector.html', grievances=grievances)

@app.route('/update_status', methods=['post'])
def update_status():
    grievance_id = request.form['grievance_id']
    status = request.form['status']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE investigations SET status = %s WHERE grievance_id = %s', (status, grievance_id))
    conn.commit()
    conn.close()
    message = 'Status updated successfully!'
    return redirect(url_for('status_selector', message=message))

@app.route('/investigation_report.html')
def submit_report_form():
    if 'id' not in session or 'role' not in session:
        flash('You must be logged in to access this page.', 'error')
        return redirect(url_for('index'))

    user_id = session['id']  # Get the logged-in investigator's ID
    role = session['role']  # Get the logged-in user's role

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
            SELECT g.grievance_id, g.description
            FROM grievances g
            JOIN grievance_assignments ga ON g.grievance_id = ga.grievance_id
            WHERE ga.investigator_id = %s
              AND ga.assigned_at = (
                  SELECT MAX(ga2.assigned_at)
                  FROM grievance_assignments ga2
                  WHERE ga2.grievance_id = g.grievance_id
              )
        ''', (user_id,))
    grievances = cursor.fetchall()
    

    
    conn.close()
    return render_template('investigation_report.html', grievances=grievances)
@app.route('/submit_report', methods=['POST'])
def submit_report():
    if 'id' not in session or 'role' not in session:
        flash('You must be logged in to submit a report.', 'error')
        return redirect(url_for('index'))

    user_id = session['id']  # Get the logged-in investigator's ID
    role = session['role']  # Get the logged-in user's role

    if role != 'investigator':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

    try:
        grievance_id = request.form['grievance_id']
        enquiry = request.form['enquiry']
        priority = request.form['priority']
        status = request.form['status']
        report = request.form['report']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if a report already exists for the given grievance_id
        cursor.execute('SELECT COUNT(*) FROM investigations WHERE grievance_id = %s', (grievance_id,))
        report_exists = cursor.fetchone()[0] > 0

        if report_exists:
            # Update the existing report
            cursor.execute('''
                UPDATE investigations 
                SET 
                    enquiry = %s,
                    priority = %s,
                    status = %s,
                    report = %s,
                    updated_at = NOW()
                WHERE grievance_id = %s
            ''', (enquiry, priority, status, report, grievance_id))
            flash('Investigation report updated successfully!', 'success')
        else:
            # Insert a new report with investigator_id
            cursor.execute('''
                INSERT INTO investigations (
                    grievance_id, 
                    investigator_id, 
                    enquiry, 
                    priority, 
                    status, 
                    report, 
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ''', (grievance_id, user_id, enquiry, priority, status, report))
            flash('Investigation report submitted successfully!', 'success')

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while submitting the report.', 'error')
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    return redirect(url_for('form_submit'))
@app.route('/view_investigations.html')
def view_investigations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM investigations')
    investigations = cursor.fetchall()
    conn.close()
    return render_template('view_investigations.html', investigations=investigations)

@app.route('/update_verdict', methods=['POST'])
def update_verdict():
    grievance_id = request.form['grievance_id']
    verdict = request.form['verdict']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE investigations SET verdict = %s WHERE grievance_id = %s', (verdict, grievance_id))
    conn.commit()
    conn.close()
    
    message = 'Verdict updated successfully!'
    return redirect(url_for('view_investigations', message=message))


@app.route('/check_verdict.html')
def check_verdict():
    if 'id' not in session or 'role' not in session:
        # Redirect to login if the user is not logged in
        flash('You must be logged in to view grievances.', 'error')
        return redirect(url_for('index'))

    user_id = session['id']  # Get the logged-in student's ID
    role = session['role']  # Get the logged-in user's role

    if role != 'student':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch grievances submitted by the logged-in student
        cursor.execute('''
            SELECT grievance_id, description
            FROM grievances
            WHERE student_id = %s
        ''', (user_id,))
        grievances = cursor.fetchall()

        conn.close()
        # Pass grievances and an optional message to the template
        return render_template('check_verdict.html', grievances=grievances, message=None)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error fetching grievances.', 'error')
        return redirect(url_for('student_dashboard'))
@app.route('/check_verdict.html', methods=['POST'])
def check_verdict_status():
    if 'id' not in session or 'role' not in session:
        flash('You must be logged in to check the verdict.', 'error')
        return redirect(url_for('index'))

    user_id = session['id']
    grievance_id = request.form.get('grievance_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT verdict, status
            FROM investigations
            WHERE grievance_id = %s
        ''', (grievance_id,))
        result = cursor.fetchone()

        # Fetch grievances for dropdown
        cursor.execute('''
            SELECT grievance_id, description
            FROM grievances
            WHERE student_id = %s
        ''', (user_id,))
        grievances = cursor.fetchall()
        conn.close()

        # Decide message based on verdict/status
        if result:
            verdict = result['verdict']
            status = result['status']
        if verdict and verdict.lower() not in ['tbd', 'pending', '']:
            flash(f"Status: {status}\\nVerdict: {verdict}\\nCorrective actions have been taken.", 'info')
        elif status and status.lower() == 'resolved':
             flash(f"Status: {status}\\nYour grievance has been resolved.", 'info')
        elif status and status.lower() == 'pending':
            flash(f"Status: {status or 'Pending'}\\nVerdict not yet decided. Please check back later.", 'warning')
        else:
            flash('No matching records found.', 'error')

        return render_template('check_verdict.html', grievances=grievances)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while checking the verdict.', 'error')
        return redirect(url_for('check_verdict'))
        
# Add this new route to your app.py
""" @app.route('/get_profile/<student_id>')
def get_profile(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Execute the query
        cursor.execute('''
            SELECT * FROM students 
            WHERE student_id = %s
        ''', (student_id,))
        
        profile = cursor.fetchone()
        
        # Check if profile exists
        if profile is None:
            flash('Profile not found!', 'error')
            return redirect(url_for('profile'))
            
        conn.close()
        return render_template('profile.html', profile=profile)
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while fetching the profile.', 'error')
        return redirect(url_for('index'))
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close() """
@app.route('/profile.html')
def profile():
    if 'id' not in session or 'role' not in session:
        print("Session variables not set. Redirecting to index.")
        return redirect(url_for('index'))
    
    user_id = session['id']
    role = session['role']

    print(f"User ID: {user_id}, Role: {role}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if role == 'student':
            # Fetch student profile
            cursor.execute('''
                SELECT student_id, name, email, mobile, gender, department, year
                FROM students
                WHERE student_id = %s
            ''', (user_id,))
        elif role == 'investigator':
            # Fetch investigator profile
            cursor.execute('''
                SELECT investigator_id, name, email, mobile, department, gender
                FROM investigators
                WHERE investigator_id = %s
            ''', (user_id,))
        else:
            flash('Invalid role!', 'error')
            return redirect(url_for('index'))
        
        profile = cursor.fetchone()
        
        if not profile:
            flash('Profile not found!', 'error')
            return render_template('profile.html', profile=None)
        
        conn.close()
        return render_template('profile.html', profile=profile, role=role)
    
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while fetching the profile.', 'error')
        return redirect(url_for('index'))
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
""" @app.route('/update_profile', methods=['POST'])
def update_profile():
   
    user_id = session['id']  # Get the logged-in user's ID
    role = session['role']  # Get the logged-in user's role

    if role != 'student':
        return jsonify({'error': 'Unauthorized access'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get form data
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        
        # Build dynamic UPDATE query based on submitted fields
        update_fields = []
        values = []
        
        if email:
            update_fields.append("email = %s")
            values.append(email)
        if mobile:
            update_fields.append("mobile = %s")
            values.append(mobile)
        if password:
            # Hash the password before storing it
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password)
            update_fields.append("password = %s")
            values.append(hashed_password)
        
        if update_fields:
            # Add user_id to values
            values.append(user_id)
            
            # Construct and execute update query
            query = f'''
                UPDATE students 
                SET {', '.join(update_fields)}
                WHERE student_id = %s
            '''
            
            cursor.execute(query, values)
            conn.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash('No fields to update!', 'warning')
        
        conn.close()
        return redirect(url_for('profile'))
    
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while updating the profile.', 'error')
        return redirect(url_for('profile'))
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close() """
""" @app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))
@app.route('/forgot_password.html')
def forgot_password():
    return render_template('forgot_password.html')
@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form['email']
    new_password = request.form['new_password']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash the new password before storing it
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(new_password)
    
    # Update the password in the database
    cursor.execute('''
        UPDATE students 
        SET password = %s 
        WHERE email = %s
    ''', (hashed_password, email))
    
    conn.commit()
    conn.close()
    
    flash('Password reset successfully!', 'success')
    return redirect(url_for('index')) """
@app.route('/dashboard_analytics.html')
def dashboard_analytics():
    return render_template('dashboard_analytics.html')
@app.route('/performance_metrics.html')
def performance_metrics():
    return render_template('performance_metrics.html')
@app.route('/generate_reports.html', methods=['GET', 'POST'])
def generate_reports():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all investigations for the report
        cursor.execute('''
SELECT 
    g.grievance_id, 
    g.student_id, 
    g.incident_date, 
    g.incident_location, 
    g.type_of_grievance, 
    
    inv.status, 
    inv.priority, 
    inv.verdict, 
    inv.report,
    inv.enquiry,                   
    i.name AS investigator_name, 
    TIMESTAMPDIFF(DAY, g.incident_date, inv.updated_at) AS resolution_time
FROM 
    grievances g
LEFT JOIN 
    investigations inv 
    ON g.grievance_id = inv.grievance_id
LEFT JOIN 
    grievance_assignments ga 
    ON g.grievance_id = ga.grievance_id
LEFT JOIN 
    investigators i 
    ON ga.investigator_id = i.investigator_id
WHERE 
    ga.assigned_at = (
        SELECT MAX(ga2.assigned_at)
        FROM grievance_assignments ga2
        WHERE ga2.grievance_id = g.grievance_id
    )
        ''')
        investigations = cursor.fetchall()

        conn.close()
        return render_template('generate_reports.html', investigations=investigations)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error generating reports.', 'error')
        return redirect(url_for('admin_dashboard'))
@app.route('/view_feedback.html')
def view_feedback():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch feedback data
        cursor.execute('''
            SELECT feedback_id, grievance_id, student_id, rating, comments, submitted_at
            FROM feedback
            ORDER BY submitted_at DESC
        ''')
        feedbacks = cursor.fetchall()

        conn.close()
        return render_template('view_feedback.html', feedbacks=feedbacks)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error fetching feedback data.', 'error')
        return redirect(url_for('admin_dashboard'))
@app.route('/toggle_activity/<string:role>/<int:user_id>', methods=['GET'])
def toggle_activity(role, user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if role == 'investigator':
            # Toggle the active status for investigators
            cursor.execute('''
                UPDATE investigators
                SET active = NOT active
                WHERE investigator_id = %s
            ''', (user_id,))
            conn.commit()
            flash('Investigator status updated successfully!', 'success')
        else:
            flash('Invalid role for toggling activity!', 'error')

        conn.close()
        return redirect(url_for('user_management'))

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error updating investigator status.', 'error')
        return redirect(url_for('user_management'))
@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get form data
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        gender = request.form['gender']
        mobile = request.form.get('mobile')  # Optional for admins
        department = request.form.get('department')  # Optional for admins
        year = request.form.get('year')  # Optional for students
        password = request.form['password']

        if role == 'investigator':
            cursor.execute('''
                INSERT INTO investigators (name, email, mobile, gender, department, password, active)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
            ''', (name, email, mobile, gender, department, password))
        elif role == 'student':
            cursor.execute('''
                INSERT INTO students (name, email, mobile, gender, department, year, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (name, email, mobile, gender, department, year, password))
        elif role == 'admin':
            cursor.execute('''
                INSERT INTO admins (name, email, gender, password)
                VALUES (%s, %s, %s, %s)
            ''', (name, email, gender, password))
        else:
            flash('Invalid role selected!', 'error')
            return redirect(url_for('user_management'))

        conn.commit()
        conn.close()

        flash('User added successfully!', 'success')
        return redirect(url_for('user_management'))

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error adding user.', 'error')
        return redirect(url_for('user_management'))
@app.route('/user_management.html')
def user_management():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all investigators
        cursor.execute('''
            SELECT investigator_id AS user_id, name, email, department, active, 'investigator' AS role
            FROM investigators
        ''')
        investigators = cursor.fetchall()

        # Fetch all admins
        cursor.execute('''
            SELECT admin_id AS user_id, name, email, NULL AS department, 1 AS active, 'admin' AS role
            FROM admins
        ''')
        admins = cursor.fetchall()

        # Fetch all students
        cursor.execute('''
            SELECT student_id AS user_id, name, email, department, 'student' AS role
            FROM students
        ''')
        students = cursor.fetchall()

        # Combine all users
        users = investigators + admins + students

        conn.close()
        return render_template('user_management.html', users=users)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error fetching user data.', 'error')
        return redirect(url_for('admin_dashboard'))
@app.route('/update_user/<string:role>/<int:user_id>', methods=['GET', 'POST'])
def update_user(role, user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            # Get form data
            name = request.form['name']
            email = request.form['email']
            mobile = request.form['mobile']
            gender = request.form['gender']
            department = request.form.get('department')  # Optional for admins
            year = request.form.get('year')  # Optional for students
            password = request.form.get('password')  # Optional for all roles

            # Update the user based on their role
            if role == 'student':
                cursor.execute('''
                    UPDATE students
                    SET name = %s, email = %s, mobile = %s, gender = %s, department = %s, year = %s, password = %s
                    WHERE student_id = %s
                ''', (name, email, mobile, gender, department, year, password, user_id))
            elif role == 'investigator':
                cursor.execute('''
                    UPDATE investigators
                    SET name = %s, email = %s, mobile = %s, gender = %s, department = %s, password = %s
                    WHERE investigator_id = %s
                ''', (name, email, mobile, gender, department, password, user_id))
            elif role == 'admin':
                # Admins can only update name, email, and mobile
                cursor.execute('''
                    UPDATE admins
                    SET name = %s, email = %s, mobile = %s
                    WHERE admin_id = %s
                ''', (name, email, mobile, user_id))
            else:
                flash('Invalid role!', 'error')
                return redirect(url_for('user_management'))


            conn.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('user_management'))

        # Fetch user details for the update form
        if role == 'student':
            cursor.execute('SELECT student_id AS user_id, name,year, department, mobile, gender,password,email FROM students WHERE student_id = %s', (user_id,))
        elif role == 'investigator':
            cursor.execute('SELECT investigator_id AS user_id, name, email, department,gender,mobile, password,active FROM investigators WHERE investigator_id = %s', (user_id,))
        elif role == 'admin':
            cursor.execute('SELECT admin_id AS user_id, name, email, password FROM admins WHERE admin_id = %s', (user_id,))
        else:
            flash('Invalid role!', 'error')
            return redirect(url_for('user_management'))

        user = cursor.fetchone()
        conn.close()

        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('user_management'))

        return render_template('update_user.html', user=user, role=role)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error updating user.', 'error')
        return redirect(url_for('user_management'))
@app.route('/student_privileges.html')
def student_privileges():
    return render_template('student_privileges.html')
@app.route('/investigator_privileges.html')
def investigator_privileges():
    return render_template('investigator_privileges.html')
@app.route('/admin_privileges.html')
def admin_privileges():
    return render_template('admin_privileges.html')
@app.route('/faqs.html')
def faqs():
    return render_template('faqs.html')

@app.route('/terms_of_service.html')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/right_to_information.html')
def right_to_information():
    return render_template('right_to_information.html')

@app.route('/guidelines.html')
def guidelines():
    return render_template('guidelines.html')

@app.route('/grievance_process.html')
def grievance_process():
    return render_template('grievance_process.html')
@app.route('/form_submit')
def form_submit():
    # Check if the user is logged in and has a role
    if 'role' not in session:
        flash('You must be logged in to access this page.', 'error')
        return redirect(url_for('index'))

    # Determine the dashboard URL based on the user's role
    role = session['role']
    if role == 'student':
        dashboard_url = url_for('student_dashboard')
    elif role == 'investigator':
        dashboard_url = url_for('investigator_dashboard')
    elif role == 'admin':
        dashboard_url = url_for('admin_dashboard')
    else:
        dashboard_url = url_for('index')  # Default fallback

    # Pass the dashboard URL to the template
    return render_template('form_submit.html', dashboard_url=dashboard_url)
@app.route('/submit_verdict', methods=['POST'])
def submit_verdict():
    if request.method != 'POST':
        flash('Invalid request method.', 'error')
        return redirect(url_for('give_verdict'))

    if 'role' not in session or session['role'] != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

    try:
        grievance_id = request.form['grievance_id']
        verdict = request.form['verdict']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the investigation with the verdict and final status
        cursor.execute('''
            UPDATE investigations
            SET verdict = %s, status = %s, updated_at = NOW()
            WHERE grievance_id = %s
        ''', (verdict, status, grievance_id))

        conn.commit()
        flash('Verdict submitted successfully!', 'success')
    except KeyError as e:
        flash(f'Missing form field: {e}', 'error')
        return redirect(url_for('give_verdict'))
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('An error occurred while submitting the verdict.', 'error')
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    return redirect(url_for('give_verdict'))
@app.route('/analytics_performance.html')
def analytics_performance():
    return render_template('analytics_performance.html')
@app.route('/give_verdict.html')
def give_verdict():
    if 'role' not in session or session['role'] != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch grievances that are pending verdict
        cursor.execute('''
            SELECT 
                inv.grievance_id, 
                g.description, 
                g.type_of_grievance, 
                g.incident_date, 
                g.incident_location, 
                inv.status, 
                inv.priority, 
                inv.verdict
            FROM investigations inv
            JOIN grievances g ON inv.grievance_id = g.grievance_id
            WHERE inv.verdict = 'TBD'
        ''')
        grievances = cursor.fetchall()

        conn.close()
        return render_template('give_verdict.html', grievances=grievances)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash('Error fetching grievances for verdict.', 'error')
        return redirect(url_for('admin_dashboard'))
if __name__ == '__main__':
    app.run(debug=True)