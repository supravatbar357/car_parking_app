# applications/routes.py
import os
from flask import send_from_directory
from flask_restful import Api
from applications.api import HomeAPI
from applications.parkinglot_api import ParkingLotsAPI
from applications.auth_api import LoginAPI, SignupAPI, ProfileAPI
from applications.parkingspot_api import ParkingSpotsAPI
from applications.reservation_api import ReservationAPI
from applications.user_api import UsersAPI
from applications.summary_api import AdminSummaryAPI, UserSummaryAPI
from applications.exports_api import ExportCSVAPI, ExportStatusAPI
from applications.worker import celery

EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)


def register_routes(api: Api):
    """Register all API endpoints with Flask-RESTful"""
    api.add_resource(HomeAPI, "/api/home")
    api.add_resource(LoginAPI, "/api/login")
    api.add_resource(SignupAPI, "/api/signup")
    api.add_resource(ProfileAPI, "/api/profile")

    # ✅ Export APIs
    api.add_resource(ExportCSVAPI, "/api/export")
    api.add_resource(ExportStatusAPI, "/api/export/status/<string:task_id>")

    # Other existing APIs
    api.add_resource(ParkingLotsAPI, "/api/parking_lots", "/api/parking_lots/<int:lot_id>")
    api.add_resource(
        ParkingSpotsAPI,
        "/api/parking_lots/<int:lot_id>/spots",
        "/api/parking_lots/<int:lot_id>/spots/<int:spot_id>",
    )
    api.add_resource(ReservationAPI, "/api/reservations", "/api/reservations/<int:reservation_id>")
    api.add_resource(UsersAPI, "/api/users", "/api/users/<int:user_id>")
    api.add_resource(AdminSummaryAPI, "/api/admin/summary")
    api.add_resource(UserSummaryAPI, "/api/user/summary")


def register_extra_routes(app):
    """Register extra non-REST routes like CSV download"""
    @app.route("/api/exports/<filename>", methods=["GET"])
    def download_export(filename):
        """Download CSV exports (async task results)"""
        return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)
