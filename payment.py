@app.route("/arctic/booking", methods=["GET", "POST"])
def arctic_booking():
    form = BookingForm()
    form.visit_time.choices = [(slot, slot) for slot in app.config["RAW_SLOTS"]]
    pricing_cfg = get_pricing_config()

    if request.method == "POST" and form.validate_on_submit():
        visit_date = form.visit_date.data
        visit_time = form.visit_time.data.strip()

        if not in_event_window(visit_date):
            flash("Selected date is outside the event window.", "error")
            return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg)
        if not valid_time_slot(visit_time):
            flash("Invalid time slot.", "error")
            return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg)

        qty_adult = form.qty_adult.data or 0
        qty_child = form.qty_child.data or 0
        qty_family = form.qty_family.data or 0
        qty_carer = form.qty_carer.data or 0

        qty_map = {
            "adult": qty_adult,
            "child": qty_child,
            "family": qty_family,
            "carer": qty_carer,
        }

        total_heads = qty_adult + qty_child + (qty_family * 4) + qty_carer

        if total_heads <= 0:
            flash("Add at least one ticket.", "error")
            return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg)

        if qty_carer and (qty_adult + qty_child + qty_family * 4) <= 0:
            flash("Carers must be booked with at least one other guest.", "error")
            return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg)

        remaining = capacity_remaining(visit_date, visit_time)
        if total_heads > remaining:
            flash(f"Not enough capacity for that slot. Remaining: {remaining}", "error")
            return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg)

        promo_code = (form.promo_code.data or "").strip()
        school_code = (pricing_cfg.get("school_promo_code") or "").strip().lower()
        if promo_code and promo_code.strip().lower() == school_code:
            children_count = qty_child + qty_family * 2
            adult_count = qty_adult + qty_family * 2
            if children_count < pricing_cfg.get("school_min_students", 0) or adult_count < 1:
                flash(f"School promo needs at least {pricing_cfg['school_min_students']} children and 1 adult.", "error")
                return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg)

        amounts = compute_booking_amounts(qty_map, promo_code, pricing_cfg)
        total_pence = amounts["total_pence"]
        requires_payment = total_pence > 0

        if requires_payment and not STRIPE_ENABLED:
            flash("Online card payments are not configured. Please contact support to complete this booking.", "error")
            return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg), 503

        booking = Booking(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip(),
            phone=form.phone.data.strip(),
            visit_date=visit_date,
            visit_time=visit_time,
            qty_adult=qty_adult,
            qty_child=qty_child,
            qty_family=qty_family,
            qty_carer=qty_carer,
            promo_code=serialize_promo_codes(promo_code),
            notes=(form.notes.data or "").strip(),
            payment_status="unpaid" if requires_payment else "paid",
            party_size=total_heads,
            amount_due_pence=total_pence,
            amount_paid_pence=0,
            booking_fee_pence=amounts["booking_fee"],
            discount_percent_applied=int(amounts["discount_percent"]),
            discount_pence=amounts["discount_pence"],
        )
        db.session.add(booking)
        db.session.flush()  # Assign an ID for Stripe metadata before committing.

        if STRIPE_ENABLED and requires_payment:
            try:
                line_items = [
                    {
                        "price_data": {
                            "currency": "gbp",
                            "product_data": {"name": "Arctic booking (incl. discounts/fees)"},
                            "unit_amount": total_pence,
                        },
                        "quantity": 1,
                    }
                ]
                base_url = current_base_url()
                session_obj = stripe.checkout.Session.create(
                    mode="payment",
                    payment_method_types=["card"],
                    line_items=line_items,
                    success_url=f"{base_url}{url_for('arctic_success')}?bid={booking.id}",
                    cancel_url=f"{base_url}{url_for('arctic_cancel')}?bid={booking.id}",
                    metadata={
                        "booking_id": str(booking.id),
                        "visit_date": str(visit_date),
                        "visit_time": visit_time,
                        "full_name": booking.full_name,
                    },
                )
                booking.stripe_checkout_id = session_obj.id
                db.session.commit()
                return redirect(session_obj.url, code=303)
            except Exception as exc:  # pragma: no cover - Stripe failure
                db.session.rollback()
                app.logger.error("Stripe checkout creation failed: %s", exc)
                flash("Unable to start the payment session. No payment has been taken.", "error")
                return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg), 502

        booking.payment_status = "paid"
        booking.amount_paid_pence = total_pence
        db.session.commit()
        return redirect(url_for("arctic_success", bid=booking.id))

    return render_template("arctic/booking.html", form=form, stripe_enabled=STRIPE_ENABLED, config=app.config, pricing=pricing_cfg)

