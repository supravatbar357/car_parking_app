# applications/worker.py
from celery import Celery
from celery.schedules import crontab
from applications.config import Config

# Initialize Celery app
celery = Celery("parking_app")

# Update Celery configuration
celery.conf.update(
    broker_url=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,
    timezone="Asia/Kolkata",
    enable_utc=False,
    beat_schedule={
        "send-daily-reminders": {
            "task": "applications.tasks.send_daily_reminders",
            "schedule": crontab(hour=18, minute=0),  # 6 PM
        },
        "send-monthly-summary": {
            "task": "applications.tasks.monthly_summary",
            "schedule": crontab(day_of_month=1, hour=9, minute=0),  # 1st day of month, 9 AM
        },
    },
)

# ✅ Import tasks AFTER Celery app is defined, so worker recognizes them
import applications.tasks  # 👈 this line registers all @celery.task decorators
