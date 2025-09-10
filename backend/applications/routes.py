from flask_restful import Api
from applications.api import HomeAPI, UserProfileAPI
from applications.parkinglot_api import ParkingLotsAPI, ExportParkingDataAPI
from applications.auth_api import LoginAPI, SignupAPI
from applications.parkingspot_api import ParkingSpotsAPI
from applications.reservation_api import ReservationAPI

def register_routes(api: Api):
    api.add_resource(LoginAPI, '/api/login')
    api.add_resource(SignupAPI, '/api/signup')
    api.add_resource(ParkingLotsAPI, '/api/parking_lots', '/api/parking_lots/<int:lot_id>')
    api.add_resource(UserProfileAPI, '/api/user/profile')
    api.add_resource(HomeAPI, '/api/home')
    api.add_resource(ParkingSpotsAPI, '/api/parking_lots/<int:lot_id>/spots','/api/parking_lots/<int:lot_id>/spots/<int:spot_id>')
    api.add_resource(ReservationAPI, '/api/reservations', '/api/reservations/<int:reservation_id>')
    api.add_resource(ExportParkingDataAPI, '/api/export-parking-data')
