from applications.worker import celery
from flask import current_app as app
from applications.models import Users, Reservation
from jinja2 import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import csv, os, smtplib

EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

def dispatch_email(receiver, subject, html_body, attachment=None):
    smtp_host, smtp_port = "localhost", 1025  # MailHog or similar
    sender = "noreply@parkingapp.com"

    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = sender, receiver, subject
    msg.attach(MIMEText(html_body, "html"))

    if attachment:
        with open(attachment, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP(host=smtp_host, port=smtp_port) as server:
            server.send_message(msg)
        print(f"[INFO] Email sent to {receiver}")
    except Exception as e:
        print(f"[ERROR] Email send failed for {receiver}: {e}")

def render_html_report(username, bookings):
    with open("templates/report.html") as f:
        template = Template(f.read())
    return template.render(username=username, bookings=bookings)

@celery.task
def send_daily_reminders():
    with app.app_context():
        users = Users.query.filter_by(is_admin=False).all()
        for user in users:
            active = Reservation.query.filter_by(user_id=user.id).count()
            msg = f"""
                <h3>Hello {user.name},</h3>
                <p>You currently have {active} active reservations.</p>
                <p>If you need parking tomorrow, please book your spot today!</p>
            """
            dispatch_email(user.email, "Daily Parking Reminder", msg)
    print("[TASK] Daily reminders sent.")

@celery.task
def monthly_summary():
    with app.app_context():
        users = Users.query.filter_by(is_admin=False).all()
        for user in users:
            bookings = Reservation.query.filter_by(user_id=user.id).all()
            report_html = render_html_report(user.name, bookings)
            dispatch_email(user.email, "Your Monthly Parking Report", report_html)
    print("[TASK] Monthly summaries emailed.")

@celery.task(bind=True)
def export_parking_data(self, parking_info, email):
    """
    Async CSV export task. Returns file path for frontend download.
    """
    csv_file = os.path.join(EXPORTS_DIR, f"parking_data_export_{self.request.id}.csv")

    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["lot_name", "spot_id", "status", "price_per_hour"])
        writer.writeheader()
        writer.writerows(parking_info)

    # Send email with attachment
    dispatch_email(
        receiver=email,
        subject="Parking Data Export Complete",
        html_body="<p>Your parking data CSV is attached.</p>",
        attachment=csv_file,
    )

    print(f"[TASK] Exported data emailed to {email}")
    # Return CSV path for frontend
    return {"csv_file": f"exports/{os.path.basename(csv_file)}"}
