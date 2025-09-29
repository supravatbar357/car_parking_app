from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)   # matches API (Signup expects 'name')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # True only for admin user

    reservations = db.relationship("Reservation", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.name} - Admin: {self.is_admin}>"

    def convert_to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin
        }


class ParkingLot(db.Model):
    __tablename__ = "parking_lots"

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)  # cost per hour
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)

    spots = db.relationship(
        "ParkingSpot",
        backref="lot",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ParkingLot {self.prime_location_name} ({self.number_of_spots} spots)>"

    def convert_to_json(self, include_spots=False):
        data = {
            "id": self.id,
            "prime_location_name": self.prime_location_name,
            "price": self.price,
            "address": self.address,
            "pin_code": self.pin_code,
            "number_of_spots": self.number_of_spots
        }
        if include_spots:
            data["spots"] = [spot.convert_to_json() for spot in self.spots]
        return data


class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"), nullable=False)
    status = db.Column(db.String(1), default="A")  # A = Available, O = Occupied

    reservations = db.relationship("Reservation", backref="spot", lazy=True)

    def __repr__(self):
        return f"<ParkingSpot {self.id} - Lot {self.lot_id} - Status {self.status}>"

    def convert_to_json(self):
        return {
            "id": self.id,
            "lot_id": self.lot_id,
            "status": self.status
        }


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    # Changed: allow NULL and set NULL if spot is deleted
    spot_id = db.Column(
        db.Integer,
        db.ForeignKey("parking_spots.id", ondelete="SET NULL"),
        nullable=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Reservation User {self.user_id} - Spot {self.spot_id} - Vehicle {self.vehicle_number}>"

    def convert_to_json(self):
        return {
            "id": self.id,
            "spot_id": self.spot_id,  # may be None if lot/spot deleted
            "user_id": self.user_id,
            "vehicle_number": self.vehicle_number,
            "parking_timestamp": self.parking_timestamp.isoformat(),
            "leaving_timestamp": self.leaving_timestamp.isoformat() if self.leaving_timestamp else None,
            "parking_cost": self.parking_cost
        }


def create_default_admin(): 
    from sqlalchemy.exc import IntegrityError

    admin_email = "admin@gmail.com"
    admin = Users.query.filter_by(email=admin_email, is_admin=True).first()

    if not admin:
        try:
            hashed_pw = generate_password_hash("admin")
            new_admin = Users(
                name="Admin",
                email=admin_email,
                password=hashed_pw,
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Default admin created")
        except IntegrityError:
            db.session.rollback()
            print("Could not create admin! Integrity Error.")
