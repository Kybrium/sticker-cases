import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

celery_app = Celery("core")
celery_app.config_from_object("core.settings", namespace="CELERY")
celery_app.conf.update(task_serializer="pickle")
celery_app.autodiscover_tasks(["packs"])

# Define beat schedule without importing tasks directly
celery_app.conf.beat_schedule = {
    "update-sticker-prices": {
        "task": "packs.tasks.update_sticker_prices_task",
        "schedule": crontab(minute=f"*/{os.getenv('CRON_MINUTES', 2)}"),  # каждые n минут
    },
}
