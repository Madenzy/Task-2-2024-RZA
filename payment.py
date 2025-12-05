import os
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
import stripe

from models import db, HotelBooking

# Configure Stripe once on import
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY") or ""
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY") or ""
stripe.api_key = STRIPE_SECRET_KEY

payment_bp = Blueprint("payment", __name__)


def _success_url(booking_id: int) -> str:
    """Build an absolute success URL for Stripe redirects."""
    return url_for("payment.hotel_payment_success", booking_id=booking_id, _external=True)


def _cancel_url(booking_id: int) -> str:
    """Build an absolute cancel URL for Stripe redirects."""
    return url_for("payment.hotel_payment_cancel", booking_id=booking_id, _external=True)


@payment_bp.route("/pay/hotel/<int:booking_id>", methods=["GET"])
@login_required
def start_hotel_checkout(booking_id: int):
    """Start a Stripe Checkout session for a hotel booking."""
    booking = HotelBooking.query.get_or_404(booking_id)

    # Only the booking owner (or admin) should pay
    if booking.user_id and booking.user_id != current_user.id and getattr(current_user, "role", "") != "admin":
        flash("You cannot pay for this booking.", "danger")
        return redirect(url_for("hotel.manage_hotel"))

    # If already paid, skip Stripe
    if booking.payment_status == "paid":
        flash("Booking already paid.", "info")
        return redirect(url_for("hotel.booking_success"))

    amount_pence = int(round(float(booking.total_price) * 100))
    # Zero-amount bookings are marked as paid automatically
    if amount_pence <= 0 or not STRIPE_SECRET_KEY:
        booking.payment_status = "paid"
        booking.payment_date = datetime.utcnow()
        db.session.commit()
        flash("Booking marked as paid.", "success")
        return redirect(url_for("hotel.booking_success"))

    try:
        session_obj = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            customer_email=getattr(current_user, "email", None),
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {"name": f"Hotel booking #{booking.id}"},
                        "unit_amount": amount_pence,
                    },
                    "quantity": 1,
                }
            ],
            success_url=_success_url(booking.id),
            cancel_url=_cancel_url(booking.id),
            metadata={"booking_id": str(booking.id)},
        )
    except Exception as exc:
        current_app.logger.error("Stripe checkout failed for booking %s: %s", booking.id, exc)
        flash("Unable to start payment, please try again.", "danger")
        return redirect(url_for("hotel.booking_failure"))

    booking.stripe_checkout_id = session_obj.id
    db.session.commit()
    return redirect(session_obj.url, code=303)


@payment_bp.route("/pay/hotel/<int:booking_id>/success", methods=["GET"])
@login_required
def hotel_payment_success(booking_id: int):
    """Handle the user returning from Stripe after a successful payment."""
    booking = HotelBooking.query.get_or_404(booking_id)
    if booking.payment_status != "paid":
        booking.payment_status = "paid"
        booking.payment_date = datetime.utcnow()
        db.session.commit()

    flash("Payment complete. Thank you!", "success")
    return redirect(url_for("hotel.booking_success"))


@payment_bp.route("/pay/hotel/<int:booking_id>/cancel", methods=["GET"])
@login_required
def hotel_payment_cancel(booking_id: int):
    """Handle a cancelled Stripe Checkout."""
    flash("Payment cancelled. You can retry from your booking list.", "warning")
    return redirect(url_for("hotel.booking_failure"))

