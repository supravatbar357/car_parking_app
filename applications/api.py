from flask import current_app as app
from flask_restful import Resource, Api 

class WelcomeApi(Resource):
    def get(self):
        return {"message": "User endpoint"}, 200
    def post(self):
        return {"message": "User created"}, 201
    