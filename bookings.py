from Flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from models import db, HotelBooking, Room, Student
from datetime import datetime
hotel_bp = Blueprint('hotel', __name__)
@hotel_bp.route('/book_hotel', methods=['GET', 'POST'])
@login_required
def book_hotel():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        room_id = request.form.get('room_id')
        check_in_date = request.form.get('check_in_date')
        check_out_date = request.form.get('check_out_date')
        number_of_guests = request.form.get('number_of_guests')

        # Fetch room to calculate total price
        room = Room.query.get(room_id)
        if not room:
            return "Room not found", 404

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

    rooms = Room.query.filter_by(availability=True).all()
    return render_template('hotel_booking.html', rooms=rooms)