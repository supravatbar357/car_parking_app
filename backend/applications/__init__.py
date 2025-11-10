from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from applications.models import db, create_default_admin
from applications.config import Config
from applications.worker import celery
from applications.api import cache


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

    # Import routes *after* app and db are ready
    from applications.routes import register_routes, register_extra_routes
    register_routes(api)
    register_extra_routes(app)

    # Import tasks *after* Celery and app setup to avoid circular imports
    from applications import tasks

    # Link Celery with Flask config
    celery.conf.update(app.config)

    return app
