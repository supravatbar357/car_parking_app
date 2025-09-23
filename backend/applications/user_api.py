from flask import request
from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from applications.models import db, Users

class UsersAPI(Resource):
    @jwt_required()
    def get(self, user_id=None):
        """Admin: Fetch all users or a single user by ID."""
        current_user_id = get_jwt_identity()
        current_user = Users.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            abort(403, message="Admin access required")

        if user_id:
            user = Users.query.get(user_id)
            if not user:
                abort(404, message="User not found")
            return user.convert_to_json(), 200

        users = Users.query.all()
        return {"users": [user.convert_to_json() for user in users]}, 200

    @jwt_required()
    def delete(self, user_id):
        """Admin: Delete a user by ID."""
        current_user_id = get_jwt_identity()
        current_user = Users.query.get(current_user_id)
        if not current_user or not current_user.is_admin:
            abort(403, message="Admin access required")

        if current_user.id == user_id:
            abort(400, message="Admin cannot delete themselves")

        user = Users.query.get(user_id)
        if not user:
            abort(404, message="User not found")

        db.session.delete(user)
        db.session.commit()
        return {"message": f"User {user_id} deleted successfully"}, 200
