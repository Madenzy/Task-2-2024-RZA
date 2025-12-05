from flask import Flask
from configure import configure_app
from models import db, Room


def _default_rooms():
   #hotel rooms to seed.
   #maximum of 6 bedrooms max capacity 4 people per room. max beds 4 per room.
  
    return [
        {
            "id": "101",
            "room_type": "family",
            "capacity": 4,
            "price_per_night": 180.00,
            "bathrooms": 2,
            "beds": 3,
            "bedrooms": 2,
            "description": "Family room with two bedrooms and a shared living area.",
        },
        {
            "id": "201",
            "room_type": "family",
            "capacity": 5,
            "price_per_night": 220.00,
            "bathrooms": 2,
            "beds": 4,
            "bedrooms": 2,
            "description": "Spacious family suite with extra bed and balcony view.",
        },
        {
            "id": "110",
            "room_type": "double",
            "capacity": 2,
            "price_per_night": 130.00,
            "bathrooms": 1,
            "beds": 1,
            "bedrooms": 1,
            "description": "Standard double room ideal for couples.",
        },
        {
            "id": "120",
            "room_type": "single",
            "capacity": 1,
            "price_per_night": 95.00,
            "bathrooms": 1,
            "beds": 1,
            "bedrooms": 1,
            "description": "Compact single room with workspace.",
        },
        {
            "id": "301",
            "room_type": "suite",
            "capacity": 3,
            "price_per_night": 260.00,
            "bathrooms": 2,
            "beds": 2,
            "bedrooms": 1,
            "description": "Suite with lounge area and premium amenities.",
        },
        {
            "id": "305",
            "room_type": "suite",
            "capacity": 4,
            "price_per_night": 300.00,
            "bathrooms": 2,
            "beds": 3,
            "bedrooms": 2,
            "description": "Luxury suite with two bedrooms and city view.",
        }
        {
            "id": "130",
            "room_type": "single",
            "capacity": 1,
            "price_per_night": 90.00,
            "bathrooms": 1,
            "beds": 1,
            "bedrooms": 1,
            "description": "Economy single room with essential amenities.",
        }
        {
            "id": "210",
            "room_type": "double",
            "capacity": 2,
            "price_per_night": 140.00,
            "bathrooms": 1,
            "beds": 1,
            "bedrooms": 1,
            "description": "Deluxe double room with modern decor.",
        },
        {
            "id": "220",
            "room_type": "double",
            "capacity": 2,
            "price_per_night": 150.00,
            "bathrooms": 1,
            "beds": 2,
            "bedrooms": 1,
            "description": "Double room with two beds and garden view.",
        },
        {
            "id": "320",
            "room_type": "suite",
            "capacity": 3,
            "price_per_night": 280.00,
            "bathrooms": 2,
            "beds": 2,
            "bedrooms": 1,
            "description": "Executive suite with work area and premium services.",
        },
        {
            "id": "330",
            "room_type": "suite",
            "capacity": 4,
            "price_per_night": 320.00,
            "bathrooms": 2,
            "beds": 3,
            "bedrooms": 2,
            "description": "Presidential suite with luxurious amenities and panoramic views.",
        },
    ]


def seed_rooms(app: Flask | None = None):
    #Seed the rooms table with a default set of hotel rooms.
    
    app = app or Flask(__name__)
    configure_app(app)

    with app.app_context():
        db.create_all()
        existing_ids = {room.id for room in Room.query.with_entities(Room.id).all()}

        new_records = []
        for room_data in _default_rooms():
            if room_data["id"] in existing_ids:
                continue
            new_records.append(Room(**room_data, availability=True))

        if not new_records:
            print("Rooms already seeded; no changes made.")
            return

        db.session.add_all(new_records)
        db.session.commit()
        print(f"Seeded {len(new_records)} room(s).")


if __name__ == "__main__":
    seed_rooms()
