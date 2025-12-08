from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import and_

from models import db, HotelBooking, Room, payment_cards

# --- Nav links used by templates ---
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

hotel_booking_links = [nav_links[i] for i in (0, 1, 3, 2, 6)]  # Home, About Us, Privacy, Logout


def filter_rooms(params):
    """Return rooms that match search criteria and are available for requested dates."""
    query = Room.query.filter_by(availability=True)

    bedrooms = params.get("bedrooms", type=int)
    bathrooms = params.get("bathrooms", type=int)
    beds = params.get("beds", type=int)
    room_type = params.get("room_type")
    guests = params.get("number_of_guests", type=int)
    check_in_str = params.get("check_in_date")
    check_out_str = params.get("check_out_date")

    if guests:
        query = query.filter(Room.capacity >= guests)
    if room_type:
        query = query.filter(Room.room_type.ilike(f"%{room_type}%"))
    if bedrooms is not None:
        query = query.filter(Room.bedrooms >= bedrooms)
    if bathrooms is not None:
        query = query.filter(Room.bathrooms >= bathrooms)
    if beds is not None:
        query = query.filter(Room.beds >= beds)

    check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date() if check_in_str else None
    check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date() if check_out_str else None

    # Exclude rooms already booked in the requested date range.
    if check_in and check_out:
        overlapping = HotelBooking.query.filter(
            and_(
                HotelBooking.check_in_date < check_out,
                HotelBooking.check_out_date > check_in,
            )
        ).all()
        booked_ids = {b.room_id for b in overlapping}
        if booked_ids:
            query = query.filter(~Room.id.in_(booked_ids))

    return query.all()


def _release_pending_booking(booking: HotelBooking):
    """Free the room and delete a pending/failed booking."""
    room = Room.query.get(booking.room_id)
    if room:
        room.availability = True
    db.session.delete(booking)
    db.session.commit()


def _amounts(booking: HotelBooking):
    base = booking.total_price or 0
    VAT = round(base * 0.2, 2)
    fee_fee = round(base * 0.02, 2)
    fyd_fee = 0
    total = round(base + VAT + fee_fee + fyd_fee, 2)
    return base, VAT, fee_fee, fyd_fee, total


hotel_bp = Blueprint("hotel", __name__)


@hotel_bp.route("/hotel_booking", methods=["GET", "POST"])
@login_required
def book_hotel():
    """Search rooms (GET) and create a pending booking (POST) before payment."""
    if request.method == "POST":
        check_in_date = request.form.get("check_in_date")
        check_out_date = request.form.get("check_out_date")
        number_of_guests = request.form.get("number_of_guests", type=int)
        room_id = request.form.get("room_id") or request.form.get("selected_rooms")

        if not check_in_date or not check_out_date:
            flash("Check-in and check-out dates are required.", "danger")
            return render_template("hotel_booking.html", rooms=filter_rooms(request.args), nav_links=hotel_booking_links)

        try:
            check_in_obj = datetime.strptime(check_in_date, "%Y-%m-%d").date()
            check_out_obj = datetime.strptime(check_out_date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "danger")
            return render_template("hotel_booking.html", rooms=filter_rooms(request.args), nav_links=hotel_booking_links)

        if check_in_obj < date.today():
            flash("Check-in date must be today or in the future.", "danger")
            return render_template("hotel_booking.html", rooms=filter_rooms(request.args), nav_links=hotel_booking_links)

        if check_out_obj <= check_in_obj:
            flash("Check-out date must be after check-in date.", "danger")
            return render_template("hotel_booking.html", rooms=filter_rooms(request.args), nav_links=hotel_booking_links)

        room = Room.query.get(room_id)
        if not room:
            flash("Room not found.", "danger")
            return render_template("hotel_booking.html", rooms=filter_rooms(request.args), nav_links=hotel_booking_links)

        # Double-check overlap for the chosen room.
        overlap = HotelBooking.query.filter(
            HotelBooking.room_id == room_id,
            HotelBooking.check_in_date < check_out_obj,
            HotelBooking.check_out_date > check_in_obj,
        ).first()
        if overlap:
            flash("Room is already booked for those dates.", "danger")
            return render_template("hotel_booking.html", rooms=filter_rooms(request.args), nav_links=hotel_booking_links)

        nights = (check_out_obj - check_in_obj).days
        total_price = nights * room.price_per_night

        booking = HotelBooking(
            user_id=current_user.id,
            room_id=room_id,
            check_in_date=check_in_obj,
            check_out_date=check_out_obj,
            number_of_guests=number_of_guests,
            total_price=total_price,
            payment_status="pending",
        )
        db.session.add(booking)
        room.availability = False
        db.session.commit()

        return redirect(url_for("hotel.start_payment", booking_id=booking.id))

    rooms = filter_rooms(request.args)
    return render_template("hotel_booking.html", rooms=rooms, nav_links=hotel_booking_links, flash=flash)


@hotel_bp.route("/booking_success")
@login_required
def booking_success():
    return render_template("booking_success.html", nav_links=hotel_booking_links)





@hotel_bp.route("/manage_hotel")
@login_required
def manage_hotel():
    bookings = HotelBooking.query.all()
    return render_template("manage_hotel.html", bookings=bookings, nav_links=hotel_booking_links)


@hotel_bp.route("/cancel_booking/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = HotelBooking.query.get(booking_id)
    if booking:
        _release_pending_booking(booking)
        flash("Booking cancelled successfully.", "success")
    else:
        flash("Booking not found.", "danger")
    return redirect(url_for("hotel.manage_hotel"))


@hotel_bp.route("/hotel_pay/<int:booking_id>", methods=["GET"])
@login_required
def start_payment(booking_id):
    """Show the fake payment page for a pending booking."""
    booking = HotelBooking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id and getattr(current_user, "role", "") != "admin":
        flash("You cannot pay for this booking.", "danger")
        return redirect(url_for("hotel.manage_hotel"))

    if booking.payment_status == "paid":
        flash("Booking already paid.", "info")
        return redirect(url_for("hotel.booking_success"))

    amount, VAT, fee_fee, fyd_fee, total_amount = _amounts(booking)

    return render_template(
        "payments.html",
        booking=booking,
        amount=amount,
        nights=(booking.check_out_date - booking.check_in_date).days,
        VAT=VAT,
        fee_fee=fee_fee,
        fyd_fee=fyd_fee,
        total_amount=total_amount,
        payment_type="hotel",
        nav_links=hotel_booking_links,
    )


@hotel_bp.route("/hotel_pay/<int:booking_id>", methods=["POST"])
@login_required
def process_payment(booking_id):
    """Validate card details against stored cards and mark booking paid or fail."""
    booking = HotelBooking.query.get_or_404(booking_id)

    if booking.payment_status == "paid":
        flash("Booking already paid.", "info")
        return redirect(url_for("hotel.booking_success"))

    number_raw = (request.form.get("Card_Number") or "").replace(" ", "")
    expiry = (request.form.get("Expiry") or "").strip()
    cvc_raw = (request.form.get("CVC") or "").strip()

    if not number_raw.isdigit() or not cvc_raw.isdigit():
        flash("Payment failed (invalid card format). Please retry.", "danger")
        return redirect(url_for("hotel.start_payment", booking_id=booking.id))

    number = int(number_raw)
    cvc = int(cvc_raw)

    query = payment_cards.query.filter_by(Card_Number=number, CVC=cvc)
    if expiry:
        query = query.filter_by(Expiry=expiry)
    card = query.first()

    # Accept payment even if card isn't found to avoid blocking users.
    if not card:
        flash("Payment failed. Please check your card details and try again.", "danger")
        return redirect(url_for("hotel.start_payment", booking_id=booking.id))

    booking.payment_status = "paid"
    booking.payment_date = datetime.utcnow()
    db.session.commit()

    flash("Payment complete. Thank you!", "success")
    return redirect(url_for("hotel.booking_success"))


def init_app(app):
    app.register_blueprint(hotel_bp)


# Placeholder blueprint (unused)
booking_bp = Blueprint("booking", __name__)
@booking_bp.route("/make_payment", methods=["GET", "POST"])
@login_required
def make_payment():
    return render_template("payment.html")
