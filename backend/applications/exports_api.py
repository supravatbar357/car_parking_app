from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from applications.models import ParkingLot, ParkingSpot
from applications.tasks import export_parking_data
from applications.worker import celery


class ExportParkingDataAPI(Resource):
    @jwt_required()
    def post(self):
        """Trigger CSV export of parking data for all lots and spots."""
        email = request.json.get("email")
        if not email:
            return {"message": "Email is required"}, 400

        parking_info = []
        lots = ParkingLot.query.all()
        for lot in lots:
            for spot in lot.spots:
                parking_info.append({
                    "lot_name": lot.prime_location_name,
                    "spot_id": spot.id,
                    "status": spot.status,
                    "price_per_hour": float(lot.price)
                })

        task = export_parking_data.delay(parking_info, email)
        return {
            "message": "Export task started. Use task_id to check status.",
            "task_id": task.id
        }, 202


class ExportStatusAPI(Resource):
    @jwt_required()
    def get(self, task_id):
        """Check status of a Celery task."""
        res = celery.AsyncResult(task_id)
        info = None
        try:
            info = res.result or res.info
        except Exception:
            info = res.info
        return {"task_id": task_id, "state": res.state, "info": info}, 200
