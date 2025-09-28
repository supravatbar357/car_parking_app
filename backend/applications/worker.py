from celery import Celery
from celery.schedules import crontab
from applications.config import Config

# Global Celery instance
celery = Celery(
    "parking_app",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=["applications.tasks"]  # auto-load tasks
)

# Celery Beat Schedule
celery.conf.beat_schedule = {
    "send-daily-reminders": {
        "task": "applications.tasks.send_daily_reminders",
        "schedule": crontab(hour=18, minute=0),  # daily at 6 PM
    },
    "send-monthly-summary": {
        "task": "applications.tasks.monthly_summary",
        "schedule": crontab(day_of_month=1, hour=9, minute=0),  # 1st of month 9 AM
    },
}
celery.conf.timezone = "Asia/Kolkata"
celery.conf.enable_utc = True
