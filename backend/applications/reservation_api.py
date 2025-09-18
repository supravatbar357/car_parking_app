from flask import current_app as app, request
from applications.models import db, Users, ParkingSpot, Reservation
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_restful import Resource, abort
from datetime import datetime, timezone
from .api import cache
from sqlalchemy.exc import SQLAlchemyError



def parse_iso_datetime(s: str) -> datetime:
    """
    Parse an ISO 8601 datetime string and return a naive UTC datetime.

    Accepts:
      - '2025-09-18T20:30:00Z'
      - '2025-09-18T20:30:00+05:30'
      - '2025-09-18T20:30:00'
    """
    if not isinstance(s, str):
        raise ValueError("Datetime must be a string")

    # Handle trailing Z (Zulu/UTC)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    dt = datetime.fromisoformat(s)

    # Convert aware datetimes to UTC, strip tzinfo
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt


class ReservationAPI(Resource):
    @jwt_required()
    def get(self, reservation_id=None):
        try:
            user_id = get_jwt_identity()
            user = Users.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            if reservation_id:
                reservation = Reservation.query.get(reservation_id)
                if not reservation or reservation.user_id != user.id:
                    return {"error": "Reservation not found"}, 404
                return reservation.convert_to_json(), 200

            reservations = Reservation.query.filter_by(user_id=user.id).all()
            return {"reservations": [res.convert_to_json() for res in reservations]}, 200

        except Exception as e:
            return {"error": "Internal server error", "details": str(e)}, 500

    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = Users.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            data = request.get_json()
            if not data:
                return {"error": "Invalid request, JSON body required"}, 400

            spot_id = data.get("spot_id")
            if not spot_id:
                return {"error": "spot_id is required"}, 400

            start_time = data.get("start_time")
            if start_time:
                try:
                    parking_dt = parse_iso_datetime(start_time)
                except Exception:
                    return {"error": "Invalid datetime format. Use ISO 8601"}, 400
            else:
                parking_dt = datetime.utcnow()

            spot = ParkingSpot.query.get(spot_id)
            if not spot:
                return {"error": "Parking spot not found"}, 404
            if spot.status != "A":
                return {"error": "Parking spot is not available"}, 400

            new_reservation = Reservation(
                user_id=user.id,
                spot_id=spot.id,
                parking_timestamp=parking_dt
            )
            spot.status = "R"  # Reserved
            db.session.add(new_reservation)
            db.session.commit()

            return new_reservation.convert_to_json(), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "details": str(e)}, 500

        except Exception as e:
            return {"error": "Internal server error", "details": str(e)}, 500

    @jwt_required()
    def patch(self, reservation_id):
        try:
            user_id = get_jwt_identity()
            user = Users.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            reservation = Reservation.query.get(reservation_id)
            if not reservation or reservation.user_id != user.id:
                return {"error": "Reservation not found"}, 404

            data = request.get_json() or {}
            action = data.get("action")

            if action == "occupied":
                reservation.spot.status = "O"
                db.session.commit()
                return {"message": "Spot marked as occupied"}, 200

            elif action == "released":
                leaving_time = data.get("leaving_time")
                if not leaving_time:
                    return {"error": "leaving_time is required"}, 400

                try:
                    leaving_dt = parse_iso_datetime(leaving_time)
                except Exception:
                    return {"error": "Invalid datetime format. Use ISO 8601"}, 400

                reservation.leaving_timestamp = leaving_dt
                duration_hours = (leaving_dt - reservation.parking_timestamp).total_seconds() / 3600
                lot_price = reservation.spot.lot.price
                reservation.parking_cost = round(duration_hours * lot_price, 2)
                reservation.spot.status = "A"

                db.session.commit()
                return reservation.convert_to_json(), 200

            else:
                return {"error": "Invalid action. Use 'occupied' or 'released'"}, 400

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "details": str(e)}, 500

        except Exception as e:
            return {"error": "Internal server error", "details": str(e)}, 500

    @jwt_required()
    def delete(self, reservation_id):
        try:
            user_id = get_jwt_identity()
            user = Users.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            reservation = Reservation.query.get(reservation_id)
            if not reservation or reservation.user_id != user.id:
                return {"error": "Reservation not found"}, 404

            if reservation.spot.status == "O":
                return {"error": "Cannot delete reservation after spot is occupied"}, 400

            db.session.delete(reservation)
            db.session.commit()
            return {"message": "Reservation deleted successfully"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "details": str(e)}, 500

        except Exception as e:
            return {"error": "Internal server error", "details": str(e)}, 500
