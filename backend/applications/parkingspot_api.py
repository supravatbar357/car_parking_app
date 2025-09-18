from flask import current_app as request
from applications.models import db, Users, ParkingLot, ParkingSpot
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort
from .api import cache 
from .task import export_parking_data

class ParkingSpotsAPI(Resource):
    @jwt_required()
    @cache.cached(timeout=300)
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
            if spot.status == "O" and spot.reservation:
                # Include reservation details for occupied spots
                spot_info["reservation"] = spot.reservation.convert_to_json()
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

        data = request.json or {}
        status = data.get("status", "").upper()
        if status not in ["A", "O"]:
            abort(400, message="Invalid status. Use 'A' or 'O'")

        spot.status = status
        db.session.commit()

        spot_data = spot.convert_to_json()
        if spot.status == "O" and spot.reservation:
            spot_data["reservation"] = spot.reservation.convert_to_json()

        return spot_data, 200

class ExportParkingDataAPI(Resource):
    @jwt_required()
    def post(self):
        email = request.json.get("email")
        if not email:
            return {"message": "Email is required"}, 400

        parking_info = []
        lots = ParkingLot.query.all()
        for lot in lots:
            for spot in lot.spots:
                parking_info.append({
                    "lot_name": lot.name,
                    "spot_id": spot.id,
                    "status": spot.status,
                    "price_per_hour": spot.price_per_hour
                })

        export_parking_data.delay(parking_info, email)
        return {"message": "Export task started. You will receive an email soon."}, 202

