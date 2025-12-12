from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ------------------ Users ------------------
class Student(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # renamed from ID to id
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200))
    dob = db.Column(db.Date)
    password = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50))  # user, admin, teacher, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return f"student-{self.id}"


# ------------------ Rooms ------------------
class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.String(100), primary_key=True)
    room_type = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    availability = db.Column(db.Boolean, default=True)
    price_per_night = db.Column(db.Float)
    description = db.Column(db.String(255))
    bathrooms = db.Column(db.Integer)
    beds = db.Column(db.Integer)
    bedrooms = db.Column(db.Integer)

    def get_id(self):
        return f"room-{self.id}"


# ------------------ Hotel Bookings ------------------
class HotelBooking(db.Model):
    __tablename__ = 'hotel_bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    room_id = db.Column(db.String(100), db.ForeignKey('rooms.id'))
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    number_of_guests = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default="unpaid")
    stripe_checkout_id = db.Column(db.String(120), default="")
    payment_date = db.Column(db.DateTime)

    user = db.relationship('Student', backref='hotel_bookings')
    room = db.relationship('Room', backref='hotel_bookings')

    def get_id(self):
        return f"hotelbooking-{self.id}"


# ------------------ Tickets ------------------
class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    visit_date = db.Column(db.Date)
    number_of_people = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default="unpaid")
    stripe_checkout_id = db.Column(db.String(120), default="")
    stripe_payment_intent = db.Column(db.String(120), default="")
    verify_token = db.Column(db.String(64), default="")

    user = db.relationship('Student', backref='tickets')

    def get_id(self):
        return f"ticket-{self.id}"


# ------------------ Rewards ------------------
class Reward(db.Model):
    __tablename__ = 'rewards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rewards_points = db.Column(db.Integer, default=0)
    rewards_level = db.Column(db.String(50), default="Bronze")
    rewards_points = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('Student', backref='rewards')
    

# ------------------ Ticket Prices ------------------
class TicketPrice(db.Model):
    __tablename__ = 'ticket_prices'
    id = db.Column(db.Integer, primary_key=True)
    adult = db.Column(db.String(50))  # e.g., Child, Adult, Senior
    child = db.Column(db.String(50))
    family = db.Column(db.String(50))

    def get_id(self):
        return f"ticketprice-{self.id}"

#-------------credit cards ------------
class payment_cards(db.Model):
    __tablename__ = 'cards'
    Card_Number = db.Column(db.String, primary_key=True)
    Card_Holder_name = db.Column(db.String(100))
    CVC = db.Column(db.Integer)
    Expiry = db.Column(db.String(8))
    Card_Type = db.Column(db.String(50))

@property
def next_level_name(self):
    levels = ["Bronze", "Silver", "Gold", "Platinum"]
    current_index = levels.index(self.rewards_level)
    return levels[current_index + 1] if current_index < len(levels)-1 else "MAX"
 
@property
def points_to_next_level(self):
    thresholds = {
        "Bronze": 100,
        "Silver": 250,
        "Gold": 500,
        "Platinum": None
    }
    next_threshold = thresholds.get(self.rewards_level)
 
    if next_threshold is None:
        return 0
 
    return max(0, next_threshold - self.rewards_points)
 
@property
def next_level_progress_percent(self):
    thresholds = {
        "Bronze": 100,
        "Silver": 250,
        "Gold": 500,
        "Platinum": 500
    }
 
    current_threshold = thresholds[self.rewards_level]
    if self.rewards_level == "Platinum":
        return 100
 
    progress = (self.rewards_points / current_threshold) * 100
    return min(100, round(progress, 2))