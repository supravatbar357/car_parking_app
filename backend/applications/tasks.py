from applications.worker import celery
from flask import current_app as app
from applications.models import Users, Reservation, ParkingLot, ParkingSpot
from jinja2 import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
import csv, os, smtplib

# ---------------- Helper Functions ----------------
def dispatch_email(receiver, subject, html_body, attachment=None):
    smtp_host, smtp_port = "localhost", 1025
    sender, sender_pass = "noreply@parkingapp.com", ""

    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = sender, receiver, subject
    msg.attach(MIMEText(html_body, "html"))

    if attachment:
        with open(attachment, "rb") as f:
            part = MIMEText(f.read(), "base64", "utf-8")
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attachment)}"')
            msg.attach(part)

    server = smtplib.SMTP(host=smtp_host, port=smtp_port)
    if sender_pass:
        server.login(sender, sender_pass)
    server.send_message(msg)
    server.quit()
    print(f"[INFO] Email sent to {receiver}")

def render_html_report(username, booking_data):
    with open("templates/report.html") as f:
        template = Template(f.read())
    return template.render(username=username, reservations=booking_data)

# ---------------- Celery Tasks ----------------
@celery.task
def send_daily_reminders():
    with app.app_context():
        users = Users.query.filter_by(is_admin=False).all()
        for user in users:
            reservations = Reservation.query.filter_by(user_id=user.id).all()
            if not reservations:
                continue
            msg = f"<h3>Hello {user.name},</h3><p>You have {len(reservations)} active parking reservations today.</p>"
            dispatch_email(user.email, "Your Parking Reservations - Reminder", msg)
    print("[TASK] Daily reminders dispatched.")

@celery.task
def monthly_summary():
    with app.app_context():
        users = Users.query.filter_by(is_admin=False).all()
        for user in users:
            bookings = Reservation.query.filter_by(user_id=user.id).all()
            booking_details = [
                [b.id, b.start_time, b.end_time, b.parking_spot_id, b.parking_spot.lot_name if b.parking_spot else "N/A"]
                for b in bookings
            ]
            report_html = render_html_report(user.name, booking_details)
            dispatch_email(user.email, "Your Monthly Parking Report", report_html)
    print("[TASK] Monthly reports sent.")

@celery.task
def export_parking_data(parking_info, email):
    csv_file = "parking_data_export.csv"
    fieldnames = ["lot_name", "spot_id", "status", "price_per_hour"]
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parking_info)

    dispatch_email(
        receiver=email,
        subject="Parking Data Export",
        html_body="<p>Attached is the exported parking lot/spot data.</p>",
        attachment=csv_file
    )
    return "[TASK] Parking data exported and mailed."
