from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
import os
import re
import shutil
import json
from datetime import date, datetime
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv() 
from werkzeug.security import generate_password_hash
from models import db, Student
from configure import configure_app
from flask_login import login_required, current_user, logout_user
from bookings import hotel_bp, booking_bp
from authentication import auth_bp, login_manager

app = Flask(__name__)
app.secret_key = 'RZA_Task_2_Secret_Key'
configure_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(hotel_bp)
app.register_blueprint(auth_bp)
# booking_bp only contains a placeholder route; keep it registered for now.
app.register_blueprint(booking_bp)




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

#----- home route----
@app.route('/')
def home():
    return render_template('index.html', nav_links=home_links)

#-------- about us -------
@app.route('/about-us')
def about_us():
    return render_template('about-us.html', nav_links=about_us_links)

#----- privacy policy --------
@app.route('/privacy')
def privacy():
    return render_template('privacy.html', nav_links=privacy_links)

#----- the animals -----
@app.route('/the_animals')
def the_animals():
    return render_template('the_animals.html', nav_links=about_us_links)


@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.execute(
        db.text("SELECT * FROM users WHERE id = :id"),
        {"id": current_user.id}
    ).fetchone()

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))

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
    #get the failure reason from query parameter
    flash('sorry bro you aint got it like that', 'danger')
    return render_template('failure.html', nav_links=dashboard_links)

@app.route('/hotel_booking')
@login_required
def hotel_booking():
    # Redirect to blueprint handler so rooms/search logic is reused.
    return redirect(url_for('hotel.book_hotel'))

@app.route('/manage_zoo')
@login_required
def manage_bookings():
    return render_template('manage_zoo.html', nav_links=zoo_booking_links)

@app.route('/manage_hotel')
@login_required
def manage_hotel():
    return render_template('manage_hotel.html', nav_links=hotel_booking_links)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
