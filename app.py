from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
from models import db, Student
from configure import configure_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from sqlalchemy.orm import joinedload


app = Flask(__name__)
app.secret_key = 'RZA_Task_2_Secret_Key'
login_manager = LoginManager()
configure_app(app)
login_manager.init_app(app)
    



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

with app.app_context():
    db.create_all()
    
    
    # Insert new user
    
    #SEED DEFAULT ADMIN USER IF NOT EXISTS
def seed_admin_user():
    admin_email = 'admin@rza.co.uk'
    # --- Prevent duplicate email registration ---
    existing = Student.query.filter_by(email='admin@rza.co.uk').first()
    if not existing:
        hashed_password = generate_password_hash('Admin@123', method='sha256')
        new_admin = db.text(
            '''INSERT INTO users (name, email, address, dob, password, phone, role, created_at)
               VALUES (:name, :email, :address, :dob, :password, :phone, :role, :created_at)'''
        )
        db.session.execute(
            new_admin,
            {
            'name': 'Admin',
            'email': admin_email,
            'address': 'Admin Address',
            'dob': date(1990, 1, 1),
            'password': hashed_password,
            'phone': '0000000000',
            'role': 'admin',
            'created_at': datetime.utcnow()
            }
        )
        db.session.commit()
        print('Default admin user created.')
    else:
        print('Admin user already exists.')
  
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



@login_manager.user_loader
def load_user(user_id):
    # user_id will be a string, like "student-1" (from your Student.get_id)
    # You need to parse it to get the real database ID
    if user_id.startswith("student-"):
        student_id = int(user_id.split("-", 1)[1])
        return Student.query.get(student_id)
    return None


@app.route('/')
def home():
    return render_template('index.html', nav_links=home_links)

@app.route('/about-us')
def about_us():
    return render_template('about-us.html', nav_links=about_us_links)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html', nav_links=privacy_links)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']

        user = db.session.execute(
            db.text("SELECT * FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if user and check_password_hash(user.password, password):
            user_obj = Student()
            user_obj.ID = user.ID
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', nav_links=login_nav_links)
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
        '''
            #--- Check if email already exists ---
            existing_user = db.session.execute(db.select(db.exists().where(db.text('email') == email))).scalar()
            if existing_user:
                flash('Email already registered. Please use a different email.', 'danger')
                return render_template('register.html', nav_links=register_links)   '''
        # Check if email already exists in the users table
        existing = db.session.execute(
            db.text("SELECT 1 FROM users WHERE email = :email LIMIT 1"),
            {"email": email}
        ).fetchone()
        if existing:
            flash('Email already registered in the system.', 'danger')
            return render_template('register.html', nav_links=register_links)
        #--- Hash the password ---
        hashed_password = generate_password_hash(password, method='sha256')
        #--- Create new user ---
        new_user = db.text(
            '''INSERT INTO users (name, email, address, dob, password, phone, role, created_at)
               VALUES (:name, :email, :address, :dob, :password, :phone, :role, :created_at)'''
        )
        db.session.execute(
            new_user,
            {
            'name': username,
            'email': email,
            'address': address,
            'dob': dob,
            'password': hashed_password,
            'phone': phone,
            'role': 'user',
            'created_at': datetime.utcnow()
            }
        )
        db.session.commit()

        flash('Registration successful! Please log in.', 'success') 





        return redirect(url_for('login'))

    return render_template('register.html', nav_links=register_links)


# ---------------------- LOGOUT ----------------------
@app.route('/logout')
@login_required
def logout():
    """Log the current user out and redirect to home."""
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))
@app.route('/account/settings')
@login_required
def account_settings():
    """Unified account management page for all authenticated users."""
    user = current_user
    user_type = get_user_type(user)
    if not user_type:
        flash('Unable to determine account type for settings.', 'danger')
        return redirect(url_for('index'))

    redirect_target = {
        'student': 'student_dashboard',
        'tutor': 'teacher_dashboard',
        'admin': 'admin_dashboard',
        'parent': 'parent_dashboard',
    }.get(user_type, 'index')

    return render_template(
        'account_settings.html',
        user=user,
        user_type=user_type,
        redirect_target=redirect_target,
    )
@app.route('/dashboard')
@login_required
def dashboard():
    #make sure only users with role 'user' can access
    user = db.session.execute(
        db.text("SELECT * FROM users WHERE ID = :id"),
        {"id": current_user.ID}
    ).fetchone()
    if user.role != 'user':
        flash('Access denied. Admins cannot access user dashboard.', 'danger')
        return redirect(url_for('admin_dashboard'))
    #make sure user is authenticated
    return render_template('dashboard.html', nav_links=dashboard_links, users=user, name=user.name)

@app.route('/admin_dashboard')
@login_required
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
