from flask import current_app as request
from applications.models import db, Users, ParkingLot, ParkingSpot, Reservation
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort
from .api import cache

class ParkingSpotsAPI(Resource):
    @jwt_required()
    @cache.memoize(timeout=60)
    def get(self, lot_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        spots_data = []
        for spot in lot.spots:
            spot_info = spot.convert_to_json()

            if spot.status == "O":
                active_reservation = Reservation.query.filter_by(
                    spot_id=spot.id, leaving_timestamp=None
                ).first()
                if active_reservation:
                    reservation_info = active_reservation.convert_to_json()
                    spot_info["reservation"] = reservation_info
                    spot_info["user_id"] = active_reservation.user_id
                    spot_info["car_number"] = getattr(active_reservation, "car_number", None)

            spots_data.append(spot_info)

        return {"parking_spots": spots_data}, 200

    @jwt_required()
    def put(self, lot_id, spot_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id).first()
        if not spot:
            abort(404, message="Parking spot not found in this lot")

        data = request.get_json() or {}
        status = data.get("status", "").upper()
        if status not in ["A", "O"]:
            abort(400, message="Invalid status. Use 'A' or 'O'")

        spot.status = status
        db.session.commit()

        # Clear cache after update
        cache.delete_memoized(ParkingSpotsAPI.get)

        spot_data = spot.convert_to_json()
        if spot.status == "O":
            active_reservation = Reservation.query.filter_by(
                spot_id=spot.id, leaving_timestamp=None
            ).first()
            if active_reservation:
                reservation_info = active_reservation.convert_to_json()
                spot_data["reservation"] = reservation_info
                spot_data["user_id"] = active_reservation.user_id
                spot_data["car_number"] = getattr(active_reservation, "car_number", None)

        return spot_data, 200

    @jwt_required()
    def delete(self, lot_id, spot_id):
        """Allow admin to delete a parking spot only if it's not occupied"""
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id).first()
        if not spot:
            abort(404, message="Parking spot not found in this lot")

        if spot.status == "O":
            active_reservation = Reservation.query.filter_by(
                spot_id=spot.id, leaving_timestamp=None
            ).first()
            details = {
                "message": "Cannot delete occupied spot",
                "reservation": active_reservation.convert_to_json() if active_reservation else None
            }
            if active_reservation:
                details["user_id"] = active_reservation.user_id
                details["car_number"] = getattr(active_reservation, "car_number", None)
            return details, 400

        db.session.delete(spot)
        db.session.commit()

        # Clear cache after deletion
        cache.delete_memoized(ParkingSpotsAPI.get)

        return {"message": "Parking spot deleted successfully"}, 200
