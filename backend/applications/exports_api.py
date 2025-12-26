# applications/exports_api.py
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from applications.tasks import export_parking_data  # ✅ updated import
from celery.result import AsyncResult
from applications.worker import celery


class ExportCSVAPI(Resource):
    @jwt_required()
    def post(self):
        """
        Trigger an async export of the current user's parking reservations.
        Body (optional): { "date_from": "...", "date_to": "...", "email": "..." }
        Returns: { "task_id": "<celery id>" }
        """
        user_id = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        filters = {}

        if data.get("date_from"):
            filters["date_from"] = data["date_from"]
        if data.get("date_to"):
            filters["date_to"] = data["date_to"]

        # enqueue Celery task
        async_result = export_parking_data.apply_async(args=(user_id, data.get("email"), filters))
        return {"task_id": async_result.id}, 202


class ExportStatusAPI(Resource):
    @jwt_required()
    def get(self, task_id):
        """
        Check status of a previously enqueued export task.
        Returns status and result info if available.
        """
        res = AsyncResult(task_id, app=celery)
        response = {"task_id": task_id, "state": res.state}

        if res.ready():
            try:
                response["result"] = res.result
            except Exception:
                response["result"] = {"error": "unable_to_fetch_result"}

        return response
