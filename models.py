from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
#initialize the database
db = SQLAlchemy()


# ------------------ User ------------------
class Student(UserMixin, db.Model):
    __tablename__ = 'users'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200))
    dob = db.Column(db.Date)
    password = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    ParentEmail = db.Column(db.String(100), db.ForeignKey('parent.ParentEmail'))
    role = db.Column(db.bool(50))  # user, 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    # Flask-Login required
    def get_id(self):
        return f"student-{self.ID}"
    
    
#---------------- Hotel Booking -------------
class HotelBooking(db.Model):
    __tablename__ = 'hotel_booking'
    bookingID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.ID'))
    roomID = db.Column(db.String(100), db.ForeignKey('rooms.ID'))
    checkInDate = db.Column(db.Date)
    checkOutDate = db.Column(db.Date)
    numberOfGuests = db.Column(db.Integer)
    totalPrice = db.Column(db.Float)
    bookingDate = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('Student', backref='hotel_bookings')
    room = db.relationship('Rooms', backref='hotel_bookings')
    def get_id(self):
        return f"hotelbooking-{self.BookingID}"
    

# ------------------ Rooms ------------------
class Rooms(db.Model):
    __tablename__ = 'rooms'
    ID = db.Column(db.String(100), primary_key=True)
    room_type = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    availability = db.Column(db.Boolean, default=True)
    price_per_night = db.Column(db.Float)
    description = db.Column(db.String(255))
    bathrooms = db.Column(db.Integer)
    beds = db.Column(db.Integer)
    bedrooms = db.Column(db.Integer)


    def get_id(self):
        return f"room-{self.ID}"
    

#------------Tickets ----------------
class Tickets(db.Model):
    __tablename__ = 'tickets'
    TicketID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.ID'))
    visitDate = db.Column(db.Date)
    numberOfPeople = db.Column(db.Integer)
    totalPrice = db.Column(db.Float)
    bookingDate = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('user', backref='tickets')
    def get_id(self):
        return f"ticket-{self.TicketID}"


# ------------------ XP ------------------
class Rewards(db.Model):
    __tablename__ = 'rewards'
    ID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('use.ID'))
    rewards_level = db.Column(db.Integer)
    rewards_points = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#-------Ticket Prices -------------
class TicketPrices(db.Model):
    __tablename__ = 'ticket_prices'
    ID = db.Column(db.Integer, primary_key=True)
    adult = db.Column(db.String(50))  # e.g., Child, Adult, Senior
    child = db.Column(db.String(50))
    family = db.Column(db.String(50))

    def get_id(self):
        return f"ticketprice-{self.ID}"

