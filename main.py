from flask import Flask, request, jsonify
from flask_restful import Api
from applications.api import WelcomeApi
from applications.models import db
import os

app = Flask(__name__)

# Base directory for SQLite
base_dir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "database.sqlite3")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize DB + API
db.init_app(app)
api = Api(app)

# Ensure tables are created
with app.app_context():
    db.create_all()
api.add_resource(WelcomeApi, '/')


if __name__ == '__main__':
    app.run(debug=True, port = 5000)