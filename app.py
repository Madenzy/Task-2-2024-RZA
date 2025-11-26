from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)



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