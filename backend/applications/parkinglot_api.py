from flask import current_app as app, request, jsonify
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from applications.models import db, Users, ParkingLot, ParkingSpot, Reservation
import re
from flask_restful import abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_restful import Resource, abort
from flask import request
from werkzeug.security import check_password_hash
from applications.models import Users

class ParkingLotsAPI(Resource):
    @jwt_required()
    def get(self):
        lots = ParkingLot.query.all()
        result = []
        for lot in lots:
            result.append({
                "id": lot.id,
                "prime_location_name": lot.prime_location_name,
                "price": lot.price,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "number_of_spots": lot.number_of_spots
            })
        return {"parking_lots": result}, 200
    
    @jwt_required()
    def post(self):
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

        if not prime_location_name or not price or not address or not pin_code or not number_of_spots:
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

        for _ in range(number_of_spots):
            spot = ParkingSpot(lot_id=new_lot.id)
            db.session.add(spot)
        db.session.commit()

        return {"message": "Parking lot created successfully", "lot_id": new_lot.id}, 201     
    
    @jwt_required()
    def put(self, lot_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        data = request.json or {}
        prime_location_name = data.get("prime_location_name", "").strip()
        price = data.get("price")
        address = data.get("address", "").strip()
        pin_code = data.get("pin_code", "").strip()
        number_of_spots = data.get("number_of_spots")

        if prime_location_name:
            lot.prime_location_name = prime_location_name
        if price:
            lot.price = price
        if address:
            lot.address = address
        if pin_code:
            lot.pin_code = pin_code
        if number_of_spots:
            difference = number_of_spots - lot.number_of_spots
            if difference > 0:
                for _ in range(difference):
                    spot = ParkingSpot(lot_id=lot.id)
                    db.session.add(spot)
            elif difference < 0:
                spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id, status="A").limit(-difference).all()
                if len(spots_to_remove) < -difference:
                    abort(400, message="Not enough available spots to remove")
                for spot in spots_to_remove:
                    db.session.delete(spot)
            lot.number_of_spots = number_of_spots

        db.session.commit()
        return {"message": "Parking lot updated successfully"}, 200
    
    @jwt_required()
    def delete(self, lot_id):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            abort(403, message="Admin access required")

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            abort(404, message="Parking lot not found")

        db.session.delete(lot)
        db.session.commit()
        return {"message": "Parking lot deleted successfully"}, 200
