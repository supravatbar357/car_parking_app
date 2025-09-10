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
from flask_caching import Cache

cache = Cache()

class HomeAPI(Resource):
    @jwt_required()
    def get(self):
        print(get_jwt_identity()).get("id")
        return {"message": "Welcome to the Parking Management System API"}, 200

class UserProfileAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()  
        try:
            user_id = int(user_id)  
        except (ValueError, TypeError):
            abort(400, message="Invalid user id in token")

        claims = get_jwt()# get additional claims

        user = Users.query.get(user_id)
        if not user:
            abort(404, message="User not found")

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": claims.get("is_admin", False)
        }, 200
    
