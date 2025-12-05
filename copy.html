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
from bookings import hotel_bp

app = Flask(__name__)
app.secret_key = 'RZA_Task_2_Secret_Key'
login_manager = LoginManager()
configure_app(app)
login_manager.init_app(app)

app.register_blueprint(hotel_bp)



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
privacy_links = [nav_links[i] for i in (0, 1, 3, 4, 5 ,2)]  # Home link only
about_us_links = [nav_links[i] for i in (0, 1, 2, 4, 5)]  # Home, Privacy
hotel_booking_links = [nav_links[i] for i in (0, 1, 3, 2, 6)]  # Home, About Us, Privacy, Logout
zoo_booking_links = [nav_links[i] for i in (0, 1, 3, 2, 6)]  # Home, About Us, Privacy, Logout

with app.app_context():
    db.create_all()
    
    
    # Insert new user
    
    #SEED DEFAULT ADMIN USER IF NOT EXISTS
def seed_admin_user():
    admin_email = 'admin@rza.co.uk'
    # --- Prevent duplicate email registration ---
    existing = Student.query.filter_by(email='admin@rza.co.uk').first()
    if not existing:
        hashed_password = generate_password_hash('Admin@123', method='scrypt')
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

@app.route('/the_animals')
def the_animals():
    return render_template('the_animals.html', nav_links=about_us_links)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']

        user = Student.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

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
        hashed_password = generate_password_hash(password, method='scrypt')
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
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

def get_user_type(user):
    """Determine the user type based on the role."""
    if user.role == 'user':
        return 'user'
    elif user.role == 'admin':
        return 'admin'
    else:
        return None
    

@app.route('/account/settings')
@login_required
def account_settings():
    """Unified account management page for all authenticated users."""
    user = current_user
    user_type = get_user_type(user)
    if not user_type:
        flash('Unable to determine account type for settings.', 'danger')
        return redirect(url_for('home'))

    redirect_target = {
        'user': 'dashboard',
        'admin': 'admin_dashboard',
    }.get(user_type, 'home')

    return render_template(
        'account_settings.html',
        user=user,
        user_type=user_type,
        redirect_target=redirect_target,
    )

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.execute(
        db.text("SELECT * FROM users WHERE id = :id"),
        {"id": current_user.id}
    ).fetchone()

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    if user.role != 'user':
        flash('Access denied. Admins cannot access user dashboard.', 'danger')
        return redirect(url_for('admin_dashboard'))

    

    return render_template(
        'dashboard.html',
        nav_links=dashboard_links,
        user=user,
        
    )


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', nav_links=admin_nav_links)

@app.route('/zoo_booking')
@login_required
def zoo_booking():
    return render_template('zoo_booking.html', nav_links=zoo_booking_links)

@app.route('/success')
@login_required
def success():
    return render_template('success.html', nav_links=dashboard_links)

@app.route('/failure')
@login_required
def failure():
    return render_template('failure.html', nav_links=dashboard_links)

@app.route('/hotel_booking')
@login_required
def hotel_booking():
    #add the functions from bookings.py to filter rooms based on user input

    return render_template('hotel_booking.html', nav_links=hotel_booking_links)

@app.route('/manage_zoo')
@login_required
def manage_bookings():
    return render_template('manage_zoo.html', nav_links=zoo_booking_links)

@app.route('/manage_hotel')
@login_required
def manage_hotel():
    return render_template('manage_hotel.html', nav_links=hotel_booking_links)


def get_user_password_hash(user):
    """Read the hashed password value regardless of concrete model."""
    return getattr(user, 'Password', None)

#go to url
def redirect_after_account_action(fallback_endpoint):
    """Redirect to the provided endpoint, preferring a user-supplied target."""
    target_endpoint = request.form.get('redirect_to')
    if target_endpoint:
        try:
            return redirect(url_for(target_endpoint))
        except Exception:
            pass
    return redirect(url_for(fallback_endpoint))

#set the new hash
def set_user_password(user, raw_password):
    """Persist a new password hash for any supported user model."""
    user.Password = generate_password_hash(raw_password, method='pbkdf2:sha256', salt_length=16)
#change_password
@app.route('/account/change-password', methods=['POST'])
@login_required
def change_password():
    """Handle password updates for every authenticated account type."""
    # Read form values
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    user = current_user
    user_type = get_user_type(user)
    if not user_type:
        flash('Unable to determine account type for password update.', 'danger')
        return redirect(url_for('index'))

    # Verify the current password matches the stored hash
    password_hash = get_user_password_hash(user)
    if not password_hash or not check_password_hash(password_hash, current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect_after_account_action(f'{user_type}_dashboard' if user_type in {'student', 'tutor', 'admin'} else 'parent_dashboard')

    if new_password != confirm_password:
        flash('New password and confirmation do not match.', 'danger')
        return redirect_after_account_action(f'{user_type}_dashboard' if user_type in {'student', 'tutor', 'admin'} else 'parent_dashboard')

    # Ensure the new password meets the password policy
    if not is_valid_password(new_password):
        flash('New password must meet the security requirements.', 'danger')
        return redirect_after_account_action(f'{user_type}_dashboard' if user_type in {'student', 'tutor', 'admin'} else 'parent_dashboard')

    # Set and persist the new password hash
    set_user_password(user, new_password)
    db.session.commit()
    flash('Password updated successfully.', 'success')

    # Redirect to a sensible dashboard for the user
    if user_type == 'user':
        return redirect_after_account_action('dashboard')
    if user_type == 'admin':
        return redirect_after_account_action('admin_dashboard')
   
#delete account function
def delete_user_account_records(user, user_type):
    """Clean up related objects before removing a user record."""
    #user acc
    if user_type == 'user':
        #remove user bookings
        bookings = db.session.execute(
            db.text("SELECT * FROM hotel_bookings WHERE user_id = :user_id"),
            {"user_id": user.id}
        ).fetchall()
        for booking in bookings:
            db.session.delete(booking)
        #delete user rewards
        rewards = db.session.execute(
            db.text("SELECT * FROM rewards WHERE user_id = :user_id"),
            {"user_id": user.id}
        ).fetchall()
        for reward in rewards:
            db.session.delete(reward)
        # Finally, delete the user record
        db.session.delete(user)
        return
   
    #admin acc
    if user_type == 'admin':
        db.session.delete(user)
@app.route('/account/delete', methods=['POST'])
@login_required
def delete_account():
    """Remove the current account after confirming their password and intent."""
    # Read submitted form values
    current_password = request.form.get('current_password', '')
    confirmation_text = request.form.get('confirm_text', '')

    # Resolve the logged-in user and their type (student/tutor/parent/admin)
    user = current_user
    user_type = get_user_type(user)
    if not user_type:
        # If we cannot determine the account type, abort and inform the user
        flash('Unable to determine account type for deletion.', 'danger')
        return redirect(url_for('index'))

    # Verify the provided current password matches the stored hash
    password_hash = get_user_password_hash(user)
    if not password_hash or not check_password_hash(password_hash, current_password):
        flash('Current password is incorrect.', 'danger')
        # Redirect back to an appropriate dashboard after failed password verification
        return redirect_after_account_action(f'{user_type}_dashboard' if user_type in {'student', 'tutor', 'admin'} else 'parent_dashboard')

    # Require explicit confirmation text "DELETE" to avoid accidental removals
    if confirmation_text.strip().upper() != 'DELETE':
        flash('Type DELETE in all caps to confirm account removal.', 'danger')
        return redirect_after_account_action(f'{user_type}_dashboard' if user_type in {'student', 'tutor', 'admin'} else 'parent_dashboard')

    # Perform cascading cleanup and remove the user record from the DB
    # delete_user_account_records handles related rows (enrollments, submissions, etc.)
    delete_user_account_records(user, user_type)
    
    # Persist changes to the database
    db.session.commit()
if __name__ == '__main__':
    app.run(debug=True)
