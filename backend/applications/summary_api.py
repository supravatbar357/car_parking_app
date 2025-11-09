from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from applications.models import db, Users, ParkingLot, ParkingSpot, Reservation
from sqlalchemy import func
from .api import cache
from collections import defaultdict
from datetime import datetime


class AdminSummaryAPI(Resource):
    @jwt_required()
    def get(self):
        """
        Admin: Get global summary including total lots, total spots,
        occupied/free spots, total reservations, total revenue, and weekly revenue trends.
        Cached for 30 seconds.
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

        # Weekly revenue trend
        reservations = Reservation.query.with_entities(
            Reservation.parking_timestamp, Reservation.parking_cost
        ).all()
        weekly_revenue = {}
        for r in reservations:
            if r.parking_timestamp and r.parking_cost:
                date = r.parking_timestamp
                week_num = date.isocalendar()[1]  # ISO week number
                key = f"{date.year}-W{week_num}"
                weekly_revenue[key] = weekly_revenue.get(key, 0) + float(r.parking_cost)

        summary = {
            "total_lots": total_lots,
            "total_spots": total_spots,
            "occupied_spots": occupied_spots,
            "free_spots": free_spots,
            "total_reservations": total_reservations,
            "total_revenue": float(total_revenue),
            "weekly_revenue": weekly_revenue,
        }

        cache.set(cache_key, summary, timeout=30)
        return summary, 200

      # Assuming you have a cache setup

class UserSummaryAPI(Resource):
    @jwt_required()
    def get(self):
        """
        User: Get personal summary including:
        - Total bookings
        - Active & past reservations
        - Total spent
        - Monthly cost trends (line chart)
        - Parking lot usage (donut chart)
        Cached per-user for 15 seconds.
        """
        user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        # Check cache first
        cache_key = f"user_summary:{user_id}"
        summary = cache.get(cache_key)
        if summary:
            return summary, 200

        # Fetch all reservations
        reservations = Reservation.query.filter_by(user_id=user.id).all()

        # Separate active and past reservations
        active_reservations = [r for r in reservations if not r.leaving_timestamp]
        past_reservations = [r for r in reservations if r.leaving_timestamp]

        # Total spent and total bookings
        total_spent = sum(r.parking_cost or 0 for r in reservations)
        total_bookings = len(reservations)

        # Monthly spending for line chart
        monthly_cost = defaultdict(float)
        for r in reservations:
            if r.parking_timestamp and r.parking_cost:
                month_label = r.parking_timestamp.strftime("%b %Y")
                monthly_cost[month_label] += r.parking_cost
        monthly_cost = dict(sorted(monthly_cost.items()))

        # Parking lot usage for donut chart
        lot_usage = defaultdict(int)
        for r in reservations:
            if r.spot_id and r.spot and r.spot.lot:
                # Use prime_location_name instead of name
                lot_usage[r.spot.lot.prime_location_name] += 1

        # Build summary response
        summary = {
            "total_bookings": total_bookings,
            "total_cost": round(total_spent, 2),
            "active": len(active_reservations),
            "past": len(past_reservations),
            "monthly_cost": monthly_cost,  # For line chart
            "lot_usage": lot_usage,        # For donut chart
        }

        # Cache for 15 seconds
        cache.set(cache_key, summary, timeout=15)
        return summary, 200