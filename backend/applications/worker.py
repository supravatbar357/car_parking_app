from celery import Celery
from celery.schedules import crontab
from applications.config import Config

# Initialize Celery without auto-importing tasks to prevent circular imports
celery = Celery(
    "parking_app",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)

celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
    beat_schedule={
        "send-daily-reminders": {
            "task": "applications.tasks.send_daily_reminders",
            "schedule": crontab(hour=18, minute=0),  # 6 PM
        },
        "send-monthly-summary": {
            "task": "applications.tasks.monthly_summary",
            "schedule": crontab(day_of_month=1, hour=9, minute=0),  # 1st of month 9 AM
        },
    },
)
