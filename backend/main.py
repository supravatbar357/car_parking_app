from flask import Flask, request, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from applications.api import LoginAPI, SignupAPI, ParkingLotsAPI, UserProfileAPI
from applications.models import db, Users, ParkingLot, ParkingSpot, Reservation, create_default_admin
from werkzeug.security import generate_password_hash
from datetime import timedelta
import os

app = Flask(__name__)

# Base directory for SQLite
base_dir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "database.sqlite3")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"]="super-secret"
app.config["JWT_SECRET_KEY"] = "jwt-super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)



# Initialize DB + API
db.init_app(app)
jwt = JWTManager(app)
api = Api(app)

# Ensure tables are created
with app.app_context():
    db.create_all()
    create_default_admin()


# Add API resources
api.add_resource(LoginAPI, '/api/login')
api.add_resource(SignupAPI, '/api/signup')
api.add_resource(ParkingLotsAPI, '/api/parking_lots', '/api/parking_lots/<int:lot_id>')
api.add_resource(UserProfileAPI, '/api/user/profile')

if __name__ == '__main__':
    app.run(debug=True, port = 5000)