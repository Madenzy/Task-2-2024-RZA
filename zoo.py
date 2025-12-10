from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user

from models import db, Ticket, payment_cards

zoo_bp = Blueprint("zoo", __name__)

# ---------------- Nav links ----------------
nav_links = [
    {"name": "Home", "url": "/"},
    {"name": "About Us", "url": "/about-us"},
    {"name": "Privacy", "url": "/privacy"},
    {"name": "Dashboard", "url": "/dashboard"},
    {"name": "Login", "url": "/login"},
    {"name": "Register", "url": "/register"},
    {"name": "Logout", "url": "/logout"},
    {"name": "Zoo Booking", "url": "/zoo_booking"},
    {"name": "Manage Zoo", "url": "/manage_zoo"},
]

# ------------------ Zoo Booking ----------------
@zoo_bp.route("/zoo_booking", methods=["GET", "POST"])
@login_required
def zoo_booking():
    if request.method == "POST":
        visit_date_str = request.form.get("visit_date")
        adult_tickets = request.form.get("adult_tickets", type=int) or 0
        child_tickets = request.form.get("child_tickets", type=int) or 0
        family_tickets = request.form.get("family_ticket", type=int) or 0

        # Validate visit date
        try:
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
            if visit_date < date.today():
                flash("Visit date must be today or in the future.", "danger")
                return render_template("zoo_booking.html", nav_links=nav_links)
        except ValueError:
            flash("Invalid date format.", "danger")
            return render_template("zoo_booking.html", nav_links=nav_links)

        # Calculate total price
        total_price = adult_tickets * 35 + child_tickets * 30 + family_tickets * 75
        number_of_people = adult_tickets + child_tickets + family_tickets * 4  # assuming family ticket = 4

        # Create pending ticket
        ticket = Ticket(
            user_id=current_user.id,
            visit_date=visit_date,
            number_of_people=number_of_people,
            total_price=total_price,
            payment_status="pending"
        )
        db.session.add(ticket)
        db.session.commit()

        return redirect(url_for("zoo.start_payment", ticket_id=ticket.id))

    return render_template("zoo_booking.html", nav_links=nav_links)


# ------------------ Zoo Payment ----------------
@zoo_bp.route("/zoo_payment/<int:ticket_id>", methods=["GET"])
@login_required
def start_payment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.user_id != current_user.id:
        flash("You cannot pay for this ticket.", "danger")
        return redirect(url_for("dashboard"))

    if ticket.payment_status == "paid":
        flash("Ticket already paid.", "info")
        return redirect(url_for("zoo.booking_success", ticket_id=ticket.id))

    # Simple breakdown
    VAT = round(ticket.total_price * 0.2, 2)
    fee = round(ticket.total_price * 0.02, 2)
    total_amount = round(ticket.total_price + VAT + fee, 2)

    return render_template(
        "zoo_payment.html",
        ticket=ticket,
        VAT=VAT,
        fee=fee,
        total_amount=total_amount,
        nav_links=nav_links
    )


@zoo_bp.route("/zoo_payment/<int:ticket_id>", methods=["POST"])
@login_required
def process_payment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.payment_status == "paid":
        flash("Ticket already paid.", "info")
        return redirect(url_for("zoo.booking_success", ticket_id=ticket.id))

    number_raw = (request.form.get("Card_Number") or "").replace(" ", "")
    expiry = (request.form.get("Expiry") or "").strip()
    cvc_raw = (request.form.get("CVC") or "").strip()

    if not number_raw.isdigit() or not cvc_raw.isdigit():
        flash("Payment failed (invalid card format).", "danger")
        return redirect(url_for("zoo.start_payment", ticket_id=ticket.id))

    number = int(number_raw)
    cvc = int(cvc_raw)

    query = payment_cards.query.filter_by(Card_Number=number, CVC=cvc)
    if expiry:
        query = query.filter_by(Expiry=expiry)
    card = query.first()

    if not card:
        flash("Payment failed. Please check your card details.", "danger")
        return redirect(url_for("zoo.start_payment", ticket_id=ticket.id))

    ticket.payment_status = "paid"
    ticket.payment_date = datetime.utcnow()
    db.session.commit()

    flash("Payment successful! Enjoy your visit.", "success")
    return redirect(url_for("zoo.booking_success", ticket_id=ticket.id))


# ------------------ Booking Success ----------------
@zoo_bp.route("/zoo_booking_success/<int:ticket_id>")
@login_required
def booking_success(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user = current_user

    if ticket.user_id != current_user.id:
        flash("You cannot view this ticket.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("zoo_success.html", ticket=ticket, nav_links=nav_links, user=user)


def init_app(app):
    app.register_blueprint(zoo_bp)
