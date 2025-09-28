from flask import current_app as app, request
from applications.models import db, Users, ParkingLot, ParkingSpot, Reservation
from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from flask import request, jsonify
from applications.tasks import export_parking_data
from .api import cache


class ParkingLotsAPI(Resource):
    @jwt_required()
    @cache.memoize(timeout=60)
    def get(self, lot_id=None):
        """Fetch parking lots. If lot_id is provided, fetch specific lot."""
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user:
            abort(403, message="User not found")

        def build_spot_data(spot):
            """Helper to attach reservation details if spot is occupied."""
            spot_info = spot.convert_to_json()
            if spot.status == "O" and spot.reservations:
                # Pick the latest reservation by timestamp
                latest_reservation = sorted(
                    spot.reservations, key=lambda r: r.parking_timestamp
                )[-1]

                spot_info["reservation"] = latest_reservation.convert_to_json()
                spot_info["user_id"] = latest_reservation.user_id
                spot_info["car_number"] = getattr(latest_reservation, "vehicle_number", None)
            return spot_info

        if lot_id:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                abort(404, message="Parking lot not found")

            spots_data = [build_spot_data(spot) for spot in lot.spots]
            return {**lot.convert_to_json(include_spots=False), "spots": spots_data}, 200

        lots = ParkingLot.query.all()
        lots_data = []
        for lot in lots:
            spots_data = [build_spot_data(spot) for spot in lot.spots]
            lots_data.append({**lot.convert_to_json(include_spots=False), "spots": spots_data})

        return {"parking_lots": lots_data}, 200

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
        if price <= 0 or number_of_spots <= 0:
            abort(400, message="Price and number_of_spots must be positive numbers")

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

        # Clear cached GET data
        cache.delete_memoized(ParkingLotsAPI.get)

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
                spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id, status="A").limit(-difference).all()
                if len(spots_to_remove) < -difference:
                    abort(
                        400,
                        message=f"Cannot reduce to {data['number_of_spots']} spots. "
                                f"Only {len(spots_to_remove)} free spots available."
                    )
                for spot in spots_to_remove:
                    db.session.delete(spot)
            lot.number_of_spots = data["number_of_spots"]

        db.session.commit()

        # Clear cache after update
        cache.delete_memoized(ParkingLotsAPI.get)

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

        # Clear cache after deletion
        cache.delete_memoized(ParkingLotsAPI.get)

        return {"message": "Parking lot deleted successfully"}, 200


from flask import request, jsonify, url_for
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from applications.models import ParkingLot, ParkingSpot
from applications.tasks import export_parking_data
from applications.worker import celery
import os

EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)  # ensure folder exists

class ExportParkingDataAPI(Resource):
    @jwt_required()
    def post(self):
        """
        Trigger CSV export of parking data for all lots and spots.
        Returns task_id to track progress.
        """
        email = request.json.get("email")
        if not email:
            return {"message": "Email is required"}, 400

        # Collect parking info
        parking_info = []
        lots = ParkingLot.query.all()
        for lot in lots:
            for spot in lot.spots:
                parking_info.append({
                    "lot_name": lot.prime_location_name,
                    "spot_id": spot.id,
                    "status": spot.status,
                    "price_per_hour": float(lot.price)
                })

        # Trigger async Celery task
        task = export_parking_data.delay(parking_info, email)

        return {
            "message": "Export task started. Use task_id to check status.",
            "task_id": task.id
        }, 202


class ExportStatusAPI(Resource):
    def get(self, task_id):
        """
        Check status of a Celery task
        """
        res = celery.AsyncResult(task_id)
        info = None
        try:
            info = res.result or res.info
        except Exception:
            info = res.info

        return {"task_id": task_id, "state": res.state, "info": info}, 200
