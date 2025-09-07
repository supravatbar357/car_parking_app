from flask import current_app as request
from flask_restful import Resource
from applications.models import db, Users, ParkingLot, ParkingSpot
from flask_restful import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort
from flask import request
from applications.models import Users

class ParkingSpotsAPI(Resource):
    @jwt_required()
    def get(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        spots = [spot.convert_to_json() for spot in lot.spots]
        return {"parking_spots": spots}, 200

    @jwt_required()
    def post(self, lot_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        data = request.json or {}
        number_of_spots = data.get("number_of_spots")
        if not number_of_spots or number_of_spots <= 0:
            abort(400, message="Invalid number of spots")

        for _ in range(number_of_spots):
            spot = ParkingSpot(lot_id=lot.id)
            db.session.add(spot)
        lot.number_of_spots += number_of_spots
        db.session.commit()

        return {"message": f"{number_of_spots} spots added to lot {lot_id}"}, 201

    @jwt_required()
    def put(self, lot_id, spot_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id).first()
        if not spot:
            abort(404, message="Parking spot not found in this lot")

        data = request.json or {}
        status = data.get("status", "").upper()
        if status not in ["A", "O"]:
            abort(400, message="Invalid status. Use 'A' or 'O'")

        spot.status = status
        db.session.commit()
        return {"message": f"Spot {spot_id} status updated to {status}"}, 200

    @jwt_required()
    def delete(self, lot_id, spot_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id).first()
        if not spot:
            abort(404, message="Parking spot not found in this lot")

        db.session.delete(spot)
        lot.number_of_spots -= 1
        db.session.commit()
        return {"message": f"Spot {spot_id} deleted successfully"}, 200
