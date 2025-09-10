import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "super-secret"
    JWT_SECRET_KEY = "jwt-super-secret"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base_dir, "database.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_REDIS_URL = 'redis://localhost:6379'
    CACHE_DEFAULT_TIMEOUT = 3000

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_TIMEZONE = 'UTC'
