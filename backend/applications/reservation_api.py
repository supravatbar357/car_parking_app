from flask import request
from applications.models import db, Users, ParkingSpot, Reservation
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone, timedelta

# Define IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

def parse_iso_datetime(s: str) -> datetime:
    """
    Parse an ISO 8601 datetime string and return a naive datetime in IST.
    """
    if not isinstance(s, str):
        raise ValueError("Datetime must be a string")

    # Handle trailing 'Z' (UTC)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    dt = datetime.fromisoformat(s)

    # Convert any tz-aware datetime to IST
    if dt.tzinfo is not None:
        dt = dt.astimezone(IST).replace(tzinfo=None)

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
                if not reservation:
                    return {"error": "Reservation not found"}, 404

                if not user.is_admin and reservation.user_id != user.id:
                    return {"error": "Reservation not found"}, 404

                return reservation.convert_to_json(), 200

            reservations = (
                Reservation.query.all()
                if user.is_admin
                else Reservation.query.filter_by(user_id=user.id).all()
            )
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
            lot_id = data.get("lot_id")
            vehicle_no = data.get("vehicle_no")

            if not lot_id or not vehicle_no:
                return {"error": "lot_id and vehicle_no are required"}, 400

            # Find first available spot in lot
            spot = ParkingSpot.query.filter_by(lot_id=lot_id, status="A").first()
            if not spot:
                return {"error": "No available spots in this lot"}, 400

            spot.status = "O"

            # Always store parking timestamp in IST (naive)
            reservation = Reservation(
                spot_id=spot.id,
                user_id=user.id,
                parking_timestamp=datetime.now(IST).replace(tzinfo=None),
                vehicle_number=vehicle_no,
            )

            db.session.add(reservation)
            db.session.commit()

            return {
                "message": "Reservation created successfully",
                "reservation": reservation.convert_to_json(),
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "details": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": "Internal server error", "details": str(e)}, 500

    @jwt_required()
    def patch(self, reservation_id):
        try:
            user_id = get_jwt_identity()
            user = Users.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            reservation = Reservation.query.get(reservation_id)
            if not reservation:
                return {"error": "Reservation not found"}, 404

            if not user.is_admin and reservation.user_id != user.id:
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

                # Calculate duration in hours
                duration_hours = (
                    (leaving_dt - reservation.parking_timestamp).total_seconds() / 3600
                )
                lot_price = reservation.spot.lot.price
                reservation.parking_cost = round(duration_hours * lot_price, 2)

                # Free the spot
                reservation.spot.status = "A"

                db.session.commit()
                return reservation.convert_to_json(), 200

            else:
                return {"error": "Invalid action. Use 'occupied' or 'released'"}, 400

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "details": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": "Internal server error", "details": str(e)}, 500

    @jwt_required()
    def delete(self, reservation_id):
        try:
            user_id = get_jwt_identity()
            user = Users.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            reservation = Reservation.query.get(reservation_id)
            if not reservation:
                return {"error": "Reservation not found"}, 404

            if not user.is_admin and reservation.user_id != user.id:
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
            db.session.rollback()
            return {"error": "Internal server error", "details": str(e)}, 500
