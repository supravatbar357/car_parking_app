from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from applications.models import db, create_default_admin
from applications.config import Config
from applications.worker import celery       # global celery
from applications.routes import register_routes, register_extra_routes
from applications.api import cache
from applications import tasks  # ensure tasks are loaded

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database
    db.init_app(app)

    # Redis Cache
    cache.init_app(app)

    # JWT Auth
    jwt = JWTManager(app)

    # Flask-RESTful API
    api = Api(app)

    with app.app_context():
        db.create_all()
        create_default_admin()

    # Register RESTful resources
    register_routes(api)

    # Register extra Flask routes (status + exports)
    register_extra_routes(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
