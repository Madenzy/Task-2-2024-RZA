from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, HotelBooking, Room, Student
from datetime import datetime



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

# Function to filter rooms based on query parameters
def _filter_rooms(query_params):

    #filtered Room query based on the incoming request arguements.

    bedrooms = query_params.get("bedrooms", type=int)
    bathrooms = query_params.get("bathrooms", type=int)
    beds = query_params.get("beds", type=int)
    room_type = query_params.get("room_type")
    guests = query_params.get("number_of_guests", type=int)
    check_in_str = query_params.get("check_in_date")
    check_out_str = query_params.get("check_out_date")

    check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date() if check_in_str else None
    check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date() if check_out_str else None

    query = Room.query.filter(Room.availability.is_(True))

    if guests:
        query = query.filter(Room.capacity >= guests)
    if room_type:
        query = query.filter(Room.room_type.ilike(room_type))
    if bedrooms is not None:
        query = query.filter(Room.bedrooms >= bedrooms)
    if bathrooms is not None:
        query = query.filter(Room.bathrooms >= bathrooms)
    if beds is not None:
        query = query.filter(Room.beds >= beds)
   
    
    # Exclude rooms already booked in the requested date range.
    if check_in and check_out:
        overlap = db.and_(
            HotelBooking.check_in_date < check_out,
            HotelBooking.check_out_date >=check_in,
        )
        query = query.filter(~Room.hotel_bookings.any(overlap))

    return query.all()


hotel_bp = Blueprint('hotel', __name__)
@hotel_bp.route('/book_hotel', methods=['GET', 'POST'])
@login_required
def book_hotel():
    if request.method == 'POST':
        check_in_date = request.form.get('check_in_date')
        check_out_date = request.form.get('check_out_date')
        number_of_guests = request.form.get('number_of_guests')
        room_id = request.form.get('room_id')
        user_id = request.form.get('user_id')

        # Fetch room to calculate total price
        room = Room.query.get(room_id)
        if not room:
            return "Room not found", 404

         #validation for date range check in date must be in the future or today and check out date must be after check in date.
        if not check_in_date and check_out_date and check_out_date > check_in_date:
            flash('Check-out date must be after checkin date', 'danger')
            return [render_template("hotel_booking.html", rooms=[], nav_links=hotel_booking_links, error="Invalid date range.")]
        if not check_in_date and check_out_date < datetime.today().date():
            flash('Check-in date must be today or in the future', 'danger')
            return [render_template("hotel_booking.html", rooms=[], nav_links=hotel_booking_links, error="Check-in date must be today or in the future.")]
        # Calculate total price (simple calculation, can be improved)
        nights = (datetime.strptime(check_out_date, '%Y-%m-%d') - datetime.strptime(check_in_date, '%Y-%m-%d')).days
        total_price = nights * room.price_per_night

        # Create booking
        booking = HotelBooking(
            user_id=user_id,
            room_id=room_id,
            check_in_date=datetime.strptime(check_in_date, '%Y-%m-%d'),
            check_out_date=datetime.strptime(check_out_date, '%Y-%m-%d'),
            number_of_guests=number_of_guests,
            total_price=total_price
        )
        db.session.add(booking)
        db.session.commit()

        return redirect(url_for('hotel.booking_success'))

    rooms = _filter_rooms(request.args)
    return render_template('hotel_booking.html', rooms=rooms, nav_links=hotel_booking_links, flash=flash)

@hotel_bp.route('/booking_success')
@login_required
def booking_success():
    return render_template('booking_success.html', nav_links=hotel_booking_links)

@hotel_bp.route('/booking_failure')
@login_required
def booking_failure():
    return render_template('booking_failure.html', nav_links=hotel_booking_links)

@hotel_bp.route('/manage_hotel')
@login_required
def manage_hotel():
    bookings = HotelBooking.query.all()
    return render_template('manage_hotel.html', bookings=bookings,  nav_links=hotel_booking_links)

@hotel_bp.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = HotelBooking.query.get(booking_id)
    if booking:
        db.session.delete(booking)
        db.session.commit()
        flash('Booking cancelled successfully.', 'success')
    else:
        flash('Booking not found.', 'danger')
    return redirect(url_for('hotel.manage_hotel'))

def init_app(app):
    app.register_blueprint(hotel_bp)


booking_bp = Blueprint('booking', __name__)
@booking_bp.route('/make_payment', methods=['GET', 'POST'])
@login_required
#the stripe payment gateway function
def make_payment():
    return render_template('zoo_booking.html')