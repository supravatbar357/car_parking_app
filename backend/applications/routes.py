from flask import send_from_directory, jsonify
from flask_restful import Api
from applications.api import HomeAPI
from applications.parkinglot_api import (
    ParkingLotsAPI,
    ExportParkingDataAPI,
    ExportStatusAPI,
)
from applications.auth_api import LoginAPI, SignupAPI, ProfileAPI
from applications.parkingspot_api import ParkingSpotsAPI
from applications.reservation_api import ReservationAPI
from applications.user_api import UsersAPI
from applications.summary_api import AdminSummaryAPI, UserSummaryAPI
from applications.worker import celery
import os

EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)  # ensure exports folder exists


def register_routes(api: Api):
    """Register all API endpoints with Flask-RESTful"""
    api.add_resource(HomeAPI, "/api/home")
    api.add_resource(LoginAPI, "/api/login")
    api.add_resource(SignupAPI, "/api/signup")
    api.add_resource(ProfileAPI, "/api/profile")
    api.add_resource(ParkingLotsAPI, "/api/parking_lots", "/api/parking_lots/<int:lot_id>")
    api.add_resource(
        ParkingSpotsAPI,
        "/api/parking_lots/<int:lot_id>/spots",
        "/api/parking_lots/<int:lot_id>/spots/<int:spot_id>",
    )
    api.add_resource(ReservationAPI, "/api/reservations", "/api/reservations/<int:reservation_id>")
    api.add_resource(ExportParkingDataAPI, "/api/export-parking-data")
    api.add_resource(UsersAPI, "/api/users", "/api/users/<int:user_id>")
    api.add_resource(AdminSummaryAPI, "/api/admin/summary")
    api.add_resource(UserSummaryAPI, "/api/user/summary")


# Extra non-REST routes (status + download)
def register_extra_routes(app):
    @app.route("/api/export_status/<task_id>", methods=["GET"])
    def export_status(task_id):
        """Check the status of an async Celery task"""
        res = celery.AsyncResult(task_id)
        info = None
        try:
            info = res.result or res.info
        except Exception:
            info = res.info
        return jsonify({"task_id": task_id, "state": res.state, "info": info})

    @app.route("/api/exports/<filename>", methods=["GET"])
    def download_export(filename):
        """Download CSV exports (async task results)"""
        # ⚠️ In production, add authentication + path validation here
        return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)
