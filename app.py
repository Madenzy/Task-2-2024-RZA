from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)


my_list = ['foo', 'bar', 'baz', 'quux']
indices = [0, 2, 3]
selected = [my_list[i] for i in indices]
print(selected) # Output: ['foo', 'baz', 'quux']


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

home = [nav_links[i] for i in (0, 1, 2)]  # Home, About Us, Privacy
login = [nav_links[i] for i in (0, 1, 2, 5)]  # Home, About Us, Privacy, Register
register = [nav_links[i] for i in (0, 1, 2, 4)]  # Home, About Us, Privacy, Login
dashboard = [nav_links[i] for i in (0, 1, 2, 6)]  # Home, About Us, Privacy, Logout
admin_nav_links = nav_links  # All links for admin
privacy = [nav_links[i] for i in (0,)]  # Home link only
about_us = [nav_links[i] for i in (0, 2)]  # Home, Privacy
hotel_booking = [nav_links[i] for i in (0, 1, 2, 6)]  # Home, About Us, Privacy, Logout
zoo_booking = [nav_links[i] for i in (0, 1, 2, 6)]  # Home, About Us, Privacy, Logout
print(login)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/dashboard')

def dashboard():
    return render_template('dashboard.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/zoo_booking')
def zoo_booking():
    return render_template('zoo_booking.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/failure')
def failure():
    return render_template('failure.html')

@app.route('/hotel_booking')
def hotel_booking():
    return render_template('hotel_booking.html')

@app.route('/manage_zoo')
def manage_bookings():
    return render_template('manage_zoo.html')

@app.route('/manage_hotel')
def manage_hotel():
    return render_template('manage_hotel.html')



if __name__ == '__main__':
    app.run(debug=True)