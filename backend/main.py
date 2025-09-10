from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from applications.models import db, create_default_admin
from applications.config import Config
from applications.worker import make_celery
from applications.routes import register_routes
from applications.api import cache

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
cache.init_app(app)
jwt = JWTManager(app)
api = Api(app)

celery = make_celery(app)

with app.app_context():
    db.create_all()
    create_default_admin()

register_routes(api)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
