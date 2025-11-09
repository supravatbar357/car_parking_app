from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from applications.models import db, create_default_admin
from applications.config import Config
from applications.worker import celery
from applications.routes import register_routes, register_extra_routes
from applications.api import cache
from applications import tasks

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend (localhost:5173)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    cache.init_app(app)

    jwt = JWTManager(app)
    api = Api(app)

    with app.app_context():
        db.create_all()
        create_default_admin()

    register_routes(api)
    register_extra_routes(app)

    return app
