from flask import current_app as app, request
from applications.models import db, Users, ParkingLot, ParkingSpot
from flask_restful import Resource, abort
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .api import cache
from .task import export_parking_data
import json


class ParkingLotsAPI(Resource):
    @jwt_required()
    def get(self):
        """Fetch all parking lots (accessible to both admin and normal users)."""
        lots = ParkingLot.query.all()
        return {"parking_lots": [lot.convert_to_json(include_spots=True) for lot in lots]}, 200

    @jwt_required()
    def post(self):
        """Admin: Add a new parking lot."""
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        data = request.json or {}
        prime_location_name = data.get("prime_location_name", "").strip()
        price = data.get("price")
        address = data.get("address", "").strip()
        pin_code = data.get("pin_code", "").strip()
        number_of_spots = data.get("number_of_spots")

        if not all([prime_location_name, price, address, pin_code, number_of_spots]):
            abort(400, message="All fields are required")

        new_lot = ParkingLot(
            prime_location_name=prime_location_name,
            price=price,
            address=address,
            pin_code=pin_code,
            number_of_spots=number_of_spots
        )
        db.session.add(new_lot)
        db.session.commit()

        # Auto-create parking spots
        for _ in range(number_of_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status="A")
            db.session.add(spot)
        db.session.commit()

        return new_lot.convert_to_json(include_spots=True), 201

    @jwt_required()
    def put(self, lot_id):
        """Admin: Update parking lot details."""
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        data = request.json or {}
        if "prime_location_name" in data:
            lot.prime_location_name = data["prime_location_name"].strip()
        if "price" in data:
            lot.price = data["price"]
        if "address" in data:
            lot.address = data["address"].strip()
        if "pin_code" in data:
            lot.pin_code = data["pin_code"].strip()
        if "number_of_spots" in data:
            difference = data["number_of_spots"] - lot.number_of_spots
            if difference > 0:
                for _ in range(difference):
                    spot = ParkingSpot(lot_id=lot.id, status="A")
                    db.session.add(spot)
            elif difference < 0:
                spots_to_remove = ParkingSpot.query.filter_by(
                    lot_id=lot.id, status="A"
                ).limit(-difference).all()
                if len(spots_to_remove) < -difference:
                    abort(400, message="Not enough available spots to remove")
                for spot in spots_to_remove:
                    db.session.delete(spot)
            lot.number_of_spots = data["number_of_spots"]

        db.session.commit()
        return lot.convert_to_json(include_spots=True), 200

    @jwt_required()
    def delete(self, lot_id):
        """Admin: Delete a parking lot only if all spots are available."""
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        # Check if any spot is occupied
        occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status="O").count()
        if occupied_spots > 0:
            abort(400, message="Cannot delete lot: some spots are still occupied")

        db.session.delete(lot)
        db.session.commit()
        return {"message": "Parking lot deleted successfully"}, 200


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
                    "price_per_hour": float(spot.price_per_hour)  # Ensure JSON serializable
                })

        # Trigger Celery task
        export_parking_data.delay(parking_info, email)

        return {
            "message": "Export task started. You will receive an email soon."
        }, 202
