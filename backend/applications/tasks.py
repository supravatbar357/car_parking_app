# applications/task.py
from applications.worker import celery
from flask import current_app as app, url_for
from applications.models import Users, Reservation, ParkingLot
from jinja2 import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import csv, os, smtplib, requests, io
from datetime import datetime, timedelta

EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

def send_via_smtp(receiver, subject, html_body, attachment_path=None):
    smtp_host = app.config.get("SMTP_HOST", "localhost")
    smtp_port = int(app.config.get("SMTP_PORT", 1025))
    sender = app.config.get("SMTP_SENDER", "noreply@parkingapp.com")

    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = sender, receiver, subject
    msg.attach(MIMEText(html_body, "html"))

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP(host=smtp_host, port=smtp_port) as server:
            server.send_message(msg)
        app.logger.info(f"Email sent to {receiver}")
        return True
    except Exception as e:
        app.logger.exception("Email send failed")
        return False

def send_via_google_chat(webhook_url, title, html_body):
    """
    Post a simple message to Google Chat incoming webhook.
    Expects webhook_url string. Format message as text (no heavy html).
    """
    if not webhook_url:
        return False
    try:
        payload = {"text": f"{title}\n\n{strip_html(html_body)}"}
        r = requests.post(webhook_url, json=payload, timeout=5)
        r.raise_for_status()
        return True
    except Exception as e:
        app.logger.exception("Google Chat webhook failed")
        return False

def send_sms_via_twilio(to_number, message):
    """
    Optional Twilio send path. Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM configured.
    If not configured this will be a no-op and return False.
    """
    account_sid = app.config.get("TWILIO_ACCOUNT_SID")
    auth_token = app.config.get("TWILIO_AUTH_TOKEN")
    from_num = app.config.get("TWILIO_FROM")
    if not (account_sid and auth_token and from_num):
        return False

    try:
        # import dynamically to avoid static analyzer errors when twilio isn't installed
        import importlib
        try:
            twilio_rest = importlib.import_module("twilio.rest")
            Client = getattr(twilio_rest, "Client")
        except Exception:
            app.logger.warning("Twilio library not installed or could not be imported; skipping SMS send")
            return False

        client = Client(account_sid, auth_token)
        client.messages.create(body=message, from_=from_num, to=to_number)
        return True
    except Exception:
        app.logger.exception("Twilio SMS send failed")
        return False

def strip_html(html):
    # very small helper to generate readable plaintext for chat/SMS
    import re
    text = re.sub("<[^<]+?>", "", html)
    return text

def dispatch_alert(user, subject, html_body, attachment=None):
    """
    Delivery strategy:
      - Prefer user's preferred channel if present (user.notification_channel),
      - else: email using SMTP.
      - Also attempt Google Chat webhook if configured globally.
      - Also attempt SMS if user.phone exists and TWILIO config present.
    """
    # 1) Attempt user-specific channel (if you modeled it)
    user_channel = getattr(user, "notification_channel", None)
    primary_result = False

    # Try Google Chat webhook per-user if present
    user_gchat = getattr(user, "google_chat_webhook", None)
    global_gchat = app.config.get("GOOGLE_CHAT_WEBHOOK")  # fallback global webhook

    if user_channel == "gchat" and user_gchat:
        primary_result = send_via_google_chat(user_gchat, subject, html_body)
    elif user_channel == "sms" and getattr(user, "phone", None):
        primary_result = send_sms_via_twilio(user.phone, strip_html(html_body))
    else:
        # Default -> email
        if getattr(user, "email", None):
            primary_result = send_via_smtp(user.email, subject, html_body, attachment)

    # Notify global webhook as well if configured and primary was not webhook (optional)
    try:
        if global_gchat and not primary_result:
            send_via_google_chat(global_gchat, subject, html_body)
    except Exception:
        app.logger.exception("fallback gchat notify failed")

    # Try SMS as a last effort if Twilio is configured and user phone exists
    try:
        if getattr(user, "phone", None):
            send_sms_via_twilio(user.phone, strip_html(html_body))
    except Exception:
        app.logger.exception("fallback sms failed")

@celery.task
def send_daily_reminders():
    """
    Two reminder scenarios:
     1) For users who have not booked recently (no reservations in the last 30 days) -> personal reminder
     2) For new parking lots created within the last 24 hours -> broadcast to all users
    """
    with app.app_context():
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        one_day_ago = now - timedelta(days=1)

        # (A) Personal reminders: users who haven't booked recently
        users = Users.query.filter_by(is_admin=False).all()
        for user in users:
            try:
                # If model has last_seen/date_of_visit, prefer that. Otherwise fall back to reservations.
                last_res = Reservation.query.filter_by(user_id=user.id).order_by(getattr(Reservation, "end_time", None).desc() if hasattr(Reservation, "end_time") else None).first()
                # If last reservation exists and ended within 30 days -> skip
                if last_res:
                    # try to extract a timestamp attribute from reservation
                    last_ts = getattr(last_res, "end_time", getattr(last_res, "start_time", None))
                    if last_ts and last_ts >= thirty_days_ago:
                        continue  # active/visited recently -> no reminder

                # otherwise send reminder
                msg = f"""
                    <h3>Hello {getattr(user, 'name', 'User')},</h3>
                    <p>We noticed you haven't booked parking recently. If you need parking tomorrow, please book your spot today.</p>
                    <p>Visit the app to reserve a slot.</p>
                """
                dispatch_alert(user, "Daily Parking Reminder", msg)
            except Exception:
                app.logger.exception(f"Failed to process daily reminder for user {user.id}")

        # (B) New parking lots: broadcast when new lots are created in last 24 hours
        new_lots = ParkingLot.query.filter(getattr(ParkingLot, "created_at", None) >= one_day_ago).all() if hasattr(ParkingLot, "created_at") else []
        if new_lots:
            summary = "<ul>"
            for lot in new_lots:
                name = getattr(lot, "name", getattr(lot, "lot_name", "Parking Lot"))
                summary += f"<li>{name}</li>"
            summary += "</ul>"
            for user in users:
                try:
                    broadcast_msg = f"""
                        <h3>Hello {getattr(user, 'name', 'User')},</h3>
                        <p>New parking locations were added recently:</p>
                        {summary}
                        <p>Book now to reserve your preferred spot.</p>
                    """
                    dispatch_alert(user, "New Parking Locations Available", broadcast_msg)
                except Exception:
                    app.logger.exception(f"Failed to broadcast new lot alert to user {user.id}")

    app.logger.info("[TASK] Daily reminders finished.")

def render_html_report(username, bookings_summary, details_html=""):
    # Use a dedicated template file if present; fallback to inline template
    tpl_path = os.path.join(os.getcwd(), "templates", "report.html")
    if os.path.exists(tpl_path):
        with open(tpl_path) as f:
            template = Template(f.read())
        return template.render(username=username, bookings=bookings_summary, details_html=details_html)
    else:
        inline = """
        <html><body>
          <h2>Monthly Parking Report for {{ username }}</h2>
          <div>
            <h3>Summary</h3>
            <ul>
              <li>Total bookings this month: {{ bookings.total_bookings }}</li>
              <li>Most used parking lot: {{ bookings.most_used_lot }}</li>
              <li>Total amount spent: {{ bookings.total_spent }}</li>
            </ul>
          </div>
          <div>
            <h3>Details</h3>
            {{ details_html|safe }}
          </div>
        </body></html>
        """
        template = Template(inline)
        return template.render(username=username, bookings=bookings_summary, details_html=details_html)

@celery.task
def monthly_summary():
    """
    Generate a monthly HTML summary for each user and email it.
    Runs on the 1st of every month (cron configured in worker).
    """
    with app.app_context():
        now = datetime.utcnow()
        # go back to previous month range
        first_of_this_month = datetime(now.year, now.month, 1)
        last_month_end = first_of_this_month - timedelta(seconds=1)
        last_month_start = datetime(last_month_end.year, last_month_end.month, 1)

        users = Users.query.filter_by(is_admin=False).all()
        for user in users:
            try:
                # Query reservations in the month
                reservations_q = Reservation.query.filter(
                    Reservation.user_id == user.id
                )
                # Filter by timestamp if model has start_time/end_time
                if hasattr(Reservation, "start_time"):
                    reservations_q = reservations_q.filter(getattr(Reservation, "start_time") >= last_month_start,
                                                          getattr(Reservation, "start_time") <= last_month_end)

                bookings = reservations_q.all()
                total_bookings = len(bookings)
                # compute total_spent if a price/cost field exists
                total_spent = 0.0
                lot_counts = {}
                details_rows = []
                for r in bookings:
                    cost = getattr(r, "price", None) or getattr(r, "cost", None) or getattr(r, "amount", None) or 0
                    try:
                        total_spent += float(cost or 0)
                    except Exception:
                        pass
                    lot_name = None
                    if hasattr(r, "parking_lot_id"):
                        lot_name = getattr(r, "parking_lot_id")  # fallback to id if name not joined
                    elif hasattr(r, "lot_name"):
                        lot_name = getattr(r, "lot_name")
                    else:
                        lot_name = "Unknown"

                    lot_counts[lot_name] = lot_counts.get(lot_name, 0) + 1

                    # Build details row defensively
                    details_rows.append({
                        "slot_id": getattr(r, "slot_id", getattr(r, "spot_id", "")),
                        "spot_id": getattr(r, "spot_id", ""),
                        "start_time": getattr(r, "start_time", ""),
                        "end_time": getattr(r, "end_time", ""),
                        "cost": cost,
                        "remarks": getattr(r, "remarks", "")
                    })

                most_used_lot = max(lot_counts.items(), key=lambda t: t[1])[0] if lot_counts else "N/A"
                bookings_summary = {
                    "total_bookings": total_bookings,
                    "most_used_lot": most_used_lot,
                    "total_spent": round(total_spent, 2)
                }

                # create details HTML table
                details_html = "<table border='1' cellpadding='4'><tr><th>slot_id</th><th>spot_id</th><th>start</th><th>end</th><th>cost</th><th>remarks</th></tr>"
                for row in details_rows:
                    details_html += f"<tr><td>{row['slot_id']}</td><td>{row['spot_id']}</td><td>{row['start_time']}</td><td>{row['end_time']}</td><td>{row['cost']}</td><td>{row['remarks']}</td></tr>"
                details_html += "</table>"

                report_html = render_html_report(getattr(user, "name", "User"), bookings_summary, details_html)
                dispatch_alert(user, "Your Monthly Parking Report", report_html)

            except Exception:
                app.logger.exception(f"Failed to generate monthly summary for user {user.id}")

    app.logger.info("[TASK] Monthly summaries finished.")


@celery.task(bind=True)
def export_parking_data(self, user_id, email=None, filters=None):
    """
    Create CSV export for user parking history.
    - user_id: id of user requesting export
    - email: optional email to send the export to; if omitted use user's email
    - filters: optional dict (date_from/date_to etc)
    Returns: { "csv_file": "<relative path>", "rows": N }
    """
    with app.app_context():
        try:
            user = Users.query.get(user_id)
            if not user:
                return {"error": "user_not_found"}

            # Query reservations for user with optional filtering
            q = Reservation.query.filter_by(user_id=user_id)
            if filters:
                if filters.get("date_from") and hasattr(Reservation, "start_time"):
                    q = q.filter(getattr(Reservation, "start_time") >= filters["date_from"])
                if filters.get("date_to") and hasattr(Reservation, "start_time"):
                    q = q.filter(getattr(Reservation, "start_time") <= filters["date_to"])

            records = q.all()

            filename = f"parking_export_user_{user_id}_{self.request.id}.csv"
            csv_path = os.path.join(EXPORTS_DIR, filename)

            fieldnames = ["slot_id", "spot_id", "start_time", "end_time", "cost", "remarks"]
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in records:
                    writer.writerow({
                        "slot_id": getattr(r, "slot_id", ""),
                        "spot_id": getattr(r, "spot_id", ""),
                        "start_time": getattr(r, "start_time", ""),
                        "end_time": getattr(r, "end_time", ""),
                        "cost": getattr(r, "price", getattr(r, "cost", "")),
                        "remarks": getattr(r, "remarks", "")
                    })

            # Send email with attachment if email provided or user.email exists
            target_email = email or getattr(user, "email", None)
            if target_email:
                send_via_smtp(target_email, "Your Parking Export is Ready", "<p>Your CSV export is attached.</p>", csv_path)

            return {"csv_file": f"exports/{filename}", "rows": len(records)}
        except Exception:
            app.logger.exception("Export job failed")
            return {"error": "export_failed"}
