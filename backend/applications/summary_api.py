from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from applications.models import db, Users, ParkingLot, ParkingSpot, Reservation
from sqlalchemy import func
from .api import cache 

from collections import defaultdict
from sqlalchemy import extract, func  # your redis cache instance


class AdminSummaryAPI(Resource):
    @jwt_required()
    def get(self):
        """
        Admin: Get global summary including total lots, total spots,
        occupied/free spots, total reservations, and total revenue.
        Cached for 30 seconds to reduce DB load.
        """
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user or not user.is_admin:
            return {"error": "Admin access required"}, 403

        cache_key = "admin_summary"
        summary = cache.get(cache_key)
        if summary:
            return summary, 200

        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(status="O").count()
        free_spots = total_spots - occupied_spots
        total_reservations = Reservation.query.count()
        total_revenue = db.session.query(func.sum(Reservation.parking_cost)).scalar() or 0

        summary = {
            "total_lots": total_lots,
            "total_spots": total_spots,
            "occupied_spots": occupied_spots,
            "free_spots": free_spots,
            "total_reservations": total_reservations,
            "total_revenue": float(total_revenue)
        }

        # cache for 30 seconds
        cache.set(cache_key, summary, timeout=30)

        return summary, 200

class UserSummaryAPI(Resource):
    @jwt_required()
    def get(self):
        """
        User: Get personal summary including active reservations,
        past bookings, total spent, monthly cost, and lot usage.
        Cached per-user for 15 seconds.
        """
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        cache_key = f"user_summary:{user_id}"
        summary = cache.get(cache_key)
        if summary:
            return summary, 200

        reservations = Reservation.query.filter_by(user_id=user.id).all()
        active_reservations = [r for r in reservations if not r.leaving_timestamp]
        past_reservations = [r for r in reservations if r.leaving_timestamp]

        total_spent = sum(r.parking_cost or 0 for r in reservations)
        total_bookings = len(reservations)

        # --- Monthly spending (bar chart)
        monthly_cost = defaultdict(float)
        for r in reservations:
            if r.parking_timestamp and r.parking_cost:
                month_label = r.parking_timestamp.strftime("%b %Y")
                monthly_cost[month_label] += r.parking_cost
        monthly_cost = dict(sorted(monthly_cost.items()))

        # --- Parking lot usage (pie chart)
        lot_usage = defaultdict(int)
        for r in reservations:
            if r.spot_id and r.spot and r.spot.lot:
                lot_usage[r.spot.lot.name] += 1

        summary = {
            "total_bookings": total_bookings,
            "total_cost": round(total_spent, 2),
            "active": len(active_reservations),
            "past": len(past_reservations),
            "monthly_cost": monthly_cost,       
            "lot_usage": lot_usage              # {"Lot A": 10, "Lot B": 5, ...}
        }

        # cache for 15 seconds
        cache.set(cache_key, summary, timeout=15)
        return summary, 200
