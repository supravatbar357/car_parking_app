from flask import request
from flask_restful import Resource, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from applications.models import Users, db
import re

class LoginAPI(Resource):
    def _validate_fields(self, email, password):
        if not email:
            abort(400, message="Email is required")
        if not password:
            abort(400, message="Password is required")

    def _validate_email(self, email):
        if "@" not in email or "." not in email:
            abort(400, message="Invalid email format")

    def post(self):
        data = request.json or {}
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        # Validations
        self._validate_fields(email, password)
        self._validate_email(email)

        # Lookup user
        user = Users.query.filter_by(email=email).first()
        if not user:
            abort(404, message="User not found")

        # Password check
        if not check_password_hash(user.password, password):
            abort(401, message="Incorrect password")

        # Create JWT token
        token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )

        return {
            "message": "User logged in successfully",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": user.is_admin
            }
        }, 200


class SignupAPI(Resource):
    def _validate_fields(self, name, email, password):
        if not name:
            abort(400, message="Name is required")
        if not email:
            abort(400, message="Email is required")
        if not password:
            abort(400, message="Password is required")

    def _validate_password(self, password):
        if len(password) < 8:
            abort(400, message="Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            abort(400, message="Password must contain at least one uppercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            abort(400, message="Password must contain at least one special character")

    def _validate_email(self, email):
        if "@" not in email or "." not in email:
            abort(400, message="Invalid email format")

        if Users.query.filter_by(email=email).first():
            abort(409, message="User already exists")

    def post(self):
        data = request.json or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        # Run validations
        self._validate_fields(name, email, password)
        self._validate_password(password)
        self._validate_email(email)

        # Create user
        hashed_pw = generate_password_hash(password)
        new_user = Users(name=name, email=email, password=hashed_pw, is_admin=False)
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User signup successful"}, 201


class ProfileAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)

        if not user:
            abort(404, message="User not found")

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin
        }, 200