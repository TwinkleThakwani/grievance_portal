import mysql.connector
from mysql.connector import Error

def test_mysql_connection():
    """Test the MySQL connection."""
    print("Starting MySQL connection test...")
    try:
        print("Attempting to connect to MySQL...")
        # Establish a connection to the MySQL database.
        connection = mysql.connector.connect(
            host='localhost',  # Change this if your MySQL server is on a different host
            user='root',  # Your MySQL username
            password='olopcs',  # Your MySQL password
            database='college'  # Optional: specify the database you want to connect to
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Successfully connected to MySQL Server version:", db_info)

            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print("You're connected to the database:", record[0])

    except Error as e:
        print("Error while connecting to MySQL:", e)

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":
    test_mysql_connection()