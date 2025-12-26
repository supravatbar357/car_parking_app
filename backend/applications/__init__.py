# applications/__init__.py
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

    # Enable CORS for frontend (you may restrict origin in production)
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

    # import tasks module to ensure Celery discovers them
    # try:
    #     from applications import tasks as tasks_module
    # except Exception:
    #     app.logger.exception("Failed to import applications.tasks (Celery tasks module)")

    # Link Celery with Flask config
    celery.conf.update(app.config)

    return app
