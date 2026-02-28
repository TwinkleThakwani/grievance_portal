// Theme Toggle Logic
const themeToggle = document.getElementById('theme-toggle');
const root = document.documentElement;

// Only run theme toggle logic if the element exists
if (themeToggle) {
    // Check for saved theme preference
    if (localStorage.getItem('theme') === 'dark') {
        root.setAttribute('data-theme', 'dark');
        themeToggle.checked = true;
    }

    // Theme switch event listener
    themeToggle.addEventListener('change', function() {
        if (this.checked) {
            root.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            root.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
    });
}

// Captcha generation
let captcha;
function generate() {
    document.getElementById("submit").value = "";
    captcha = document.getElementById("image");
    let uniquechar = "";
    const randomchar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    
    for (let i = 1; i < 5; i++) {
        uniquechar += randomchar.charAt(Math.random() * randomchar.length);
    }
    
    captcha.innerHTML = uniquechar;
}

function printmsg() {
    const usr_input = document.getElementById("submit").value;
    if (usr_input == captcha.innerHTML) {
        document.getElementById("key").innerHTML = "Matched";
        document.getElementById("complaintForm").submit();
    } else {
        document.getElementById("key").innerHTML = "Not Matched";
        generate();
    }
}

// Witness form handling
const addWitnessButton = document.getElementById('addWitness');
if (addWitnessButton) {
    addWitnessButton.addEventListener('click', function() {
        const witnessCount = document.querySelectorAll('.witness').length;
        const newWitness = document.createElement('div');
        newWitness.classList.add('witness');
        newWitness.innerHTML = `
            <label for="witness_name_${witnessCount}">Witness Name:</label>
            <input type="text" id="witness_name_${witnessCount}" name="witness_name[]" required>
            
            <label for="witness_contact_${witnessCount}">Witness Contact Number:</label>
            <input type="tel" id="witness_contact_${witnessCount}" name="witness_contact[]" required>
            
            <label for="witness_involvement_${witnessCount}">How are they involved?</label>
            <textarea id="witness_involvement_${witnessCount}" name="witness_involvement[]" rows="2" required></textarea>
        `;
        document.getElementById('witnesses').appendChild(newWitness);
    });
}

// Loading animation
window.addEventListener('load', function() {
    const loader = document.querySelector('.loader');
    setTimeout(() => {
        loader.style.display = 'none';
    }, 2000);
});

// Cursor trail effect
document.addEventListener('mousemove', function(e) {
    const trail = document.createElement('div');
    trail.className = 'cursor-trail';
    trail.style.left = e.pageX + 'px';
    trail.style.top = e.pageY + 'px';
    
    // Add multiple trailing particles
    for (let i = 0; i < 3; i++) {
        const particle = trail.cloneNode();
        particle.style.width = (8 - i * 2) + 'px';
        particle.style.height = (8 - i * 2) + 'px';
        particle.style.left = (e.pageX - i * 4) + 'px';
        particle.style.top = (e.pageY - i * 4) + 'px';
        document.body.appendChild(particle);
        
        setTimeout(() => {
            particle.remove();
        }, 500 - i * 100);
    }
});
function toggleAnimation() {
    const animationToggle = document.getElementById('animation-toggle');
    const header = document.querySelector('.header');
    
    if (animationToggle.checked) {
        header.classList.add('stripe-animation');
    } else {
        header.classList.remove('stripe-animation');
    }

}

function redirectTo(page) {
    window.location.href = `/${page}`;
}

    function toggleActivity(userId, role) {
        // Redirect to toggle activity endpoint with role
        window.location.href = `/toggle_activity/${role}/${userId}`;
    }
