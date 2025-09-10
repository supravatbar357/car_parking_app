from flask import current_app as app, request
from applications.models import db, Users, ParkingSpot, Reservation
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_restful import Resource, abort
from datetime import datetime
from .api import cache

class ReservationAPI(Resource):
    @jwt_required()
    @cache.cached(timeout=300)
    def get(self, reservation_id=None):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user:
            abort(404, message="User not found")

        if reservation_id:
            reservation = Reservation.query.get(reservation_id)
            if not reservation or reservation.user_id != user.id:
                abort(404, message="Reservation not found")
            return reservation.convert_to_json(), 200

        reservations = Reservation.query.filter_by(user_id=user.id).all()
        return {"reservations": [res.convert_to_json() for res in reservations]}, 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user:
            abort(404, message="User not found")

        data = request.json or {}
        start_time = data.get("start_time")

        if not start_time:
            abort(400, message="start_time is required")

        try:
            start_time_dt = datetime.fromisoformat(start_time)
        except Exception:
            abort(400, message="Invalid datetime format. Use ISO 8601")

        # Assign first available spot automatically
        spot = ParkingSpot.query.filter_by(status="A").first()
        if not spot:
            abort(400, message="No available parking spots")

        new_reservation = Reservation(
            user_id=user.id,
            spot_id=spot.id,
            parking_timestamp=start_time_dt
        )
        db.session.add(new_reservation)
        db.session.commit()

        return new_reservation.convert_to_json(), 201

    @jwt_required()
    def patch(self, reservation_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user:
            abort(404, message="User not found")

        reservation = Reservation.query.get(reservation_id)
        if not reservation or reservation.user_id != user.id:
            abort(404, message="Reservation not found")

        data = request.json or {}
        action = data.get("action")

        if action == "occupied":
            reservation.spot.status = "O"  # Vehicle parked
            db.session.commit()
            return {"message": "Spot marked as occupied"}, 200

        elif action == "released":
            leaving_time = data.get("leaving_time")
            if not leaving_time:
                abort(400, message="leaving_time is required")

            try:
                leaving_dt = datetime.fromisoformat(leaving_time)
            except Exception:
                abort(400, message="Invalid datetime format. Use ISO 8601")

            reservation.leaving_timestamp = leaving_dt
            duration_hours = (leaving_dt - reservation.parking_timestamp).total_seconds() / 3600

            lot_price = reservation.spot.lot.price
            reservation.parking_cost = round(duration_hours * lot_price, 2)

            reservation.spot.status = "A"  # Free spot
            db.session.commit()
            return reservation.convert_to_json(), 200

        else:
            abort(400, message="Invalid action. Use 'occupied' or 'released'")

    @jwt_required()
    def delete(self, reservation_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user:
            abort(404, message="User not found")

        reservation = Reservation.query.get(reservation_id)
        if not reservation or reservation.user_id != user.id:
            abort(404, message="Reservation not found")

        if reservation.spot.status == "O":
            abort(400, message="Cannot delete reservation after spot is occupied")

        db.session.delete(reservation)
        db.session.commit()

        return {"message": "Reservation deleted successfully"}, 200
