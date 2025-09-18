from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_caching import Cache

cache = Cache()

class HomeAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        return {
            "message": "Welcome to the Parking Management System API",
            "user_id": user_id
        }, 200
