from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
from models import db

app = Flask(__name__)
app.secret_key = 'RZA_Task_2_Secret_Key'

my_list = ['foo', 'bar', 'baz', 'quux']
indices = [0, 2, 3]
selected = [my_list[i] for i in indices]
print(selected) # Output: ['foo', 'baz', 'quux']

#--- nav links setup ---
nav_links = [
    {"name": "Home", "url": "/"},
    {"name": "About Us", "url": "/about-us"},
    {"name": "Privacy", "url": "/privacy"},
    {"name": "Dashboard", "url": "/dashboard"},
    {"name": "Login", "url": "/login"},
    {"name": "Register", "url": "/register"},
    {"name": "Logout", "url": "/logout"},
    {"name": "Admin Dashboard", "url": "/admin_dashboard"},
    {"name": "Zoo Booking", "url": "/zoo_booking"},
    {"name": "Hotel Booking", "url": "/hotel_booking"},
    {"name": "Manage Zoo", "url": "/manage_zoo"},
    {"name": "Manage Hotel", "url": "/manage_hotel"},
    {"name": "Success", "url": "/success"},
    {"name": "Failure", "url": "/failure"},
    ]

home_links = [nav_links[i] for i in ( 1, 2)]  # Home, About Us, Privacy
login_nav_links = [nav_links[i] for i in (0, 1, 5, 2)]
register_links = [nav_links[i] for i in (0, 1, 2, 4)]  # Home, About Us, Privacy, Login
dashboard_links = [nav_links[i] for i in ( 8,9,1, 2,6)]  # Home, About Us, Privacy, Logout
admin_nav_links = nav_links  # All links for admin
privacy_links = [nav_links[i] for i in (0,)]  # Home link only
about_us_links = [nav_links[i] for i in (0, 2)]  # Home, Privacy
hotel_booking_links = [nav_links[i] for i in (0, 1, 2, 6)]  # Home, About Us, Privacy, Logout
zoo_booking_links = [nav_links[i] for i in (0, 1, 2, 6)]  # Home, About Us, Privacy, Logout

def is_valid_password(password):
    """
    Validate that the password:
    - Has at least 1 uppercase letter
    - Has at least 1 lowercase letter
    - Has at least 1 number
    - Has at least 1 special character
    - Is at least 8 characters long
    """
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
    return bool(re.match(pattern, password))


@app.route('/')
def home():
    return render_template('index.html', nav_links=home_links)

@app.route('/about-us')
def about_us():
    return render_template('about-us.html', nav_links=about_us_links)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html', nav_links=privacy_links)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', nav_links=dashboard_links)



@app.route('/login')
def login():
    return render_template('login.html', nav_links=login_nav_links)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'].lower()
        phone = request.form['phone']
        dob_str = request.form['dob']
        address = request.form['address']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')

        # ------------------------ VALIDATIONS ------------------------
        #check that name is correct
        if not username or len(username) < 2:
            flash('Please enter a valid name (at least 2 characters).', 'danger')
            return render_template('register.html', nav_links=register_links)
        # --- Validate passwords ---
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', nav_links=register_links)
        if not username.isalpha():
            flash('Username must contain only alphabetic characters.', 'danger')
            return render_template('register.html', nav_links=register_links)
        
        #--- Validate password strength ---
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('register.html', nav_links=register_links)
        #----validate dob to make sure its not in the future or they are at least 16years--- 
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if dob > today:
            flash('Date of Birth cannot be in the future.', 'danger')
            return render_template('register.html', nav_links=register_links)
        if age < 16:
            flash('You must be at least 16 years old to register.', 'danger')
            return render_template('register.html', nav_links=register_links)
        
        #------- age validation max age 100years --- 
        if age > 100:
            flash('Please enter a valid Date of Birth. You cannot be 100yrs old', 'danger')
            return render_template('register.html', nav_links=register_links)
        
        #------- Validate address ---
        if not address or len(address) < 5:
            flash('Please enter a valid address (at least 5 characters).', 'danger')
            return render_template('register.html', nav_links=register_links)
        
        if not is_valid_password(password):
            flash('Password must contain at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character.', 'danger')
            return render_template('register.html', nav_links=register_links)









        return redirect(url_for('login'))

    return render_template('register.html', nav_links=register_links)

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html', nav_links=admin_nav_links)

@app.route('/zoo_booking')
def zoo_booking():
    return render_template('zoo_booking.html', nav_links=zoo_booking_links)

@app.route('/success')
def success():
    return render_template('success.html', nav_links=dashboard_links)

@app.route('/failure')
def failure():
    return render_template('failure.html', nav_links=dashboard_links)

@app.route('/hotel_booking')
def hotel_booking():
    return render_template('hotel_booking.html', nav_links=hotel_booking_links)

@app.route('/manage_zoo')
def manage_bookings():
    return render_template('manage_zoo.html', nav_links=zoo_booking_links)

@app.route('/manage_hotel')
def manage_hotel():
    return render_template('manage_hotel.html', nav_links=hotel_booking_links)



if __name__ == '__main__':
    app.run(debug=True)
