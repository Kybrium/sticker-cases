import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

celery_app = Celery("core")
celery_app.config_from_object("django.core:settings", namespace="CELERY")
celery_app.conf.update(task_serializer="pickle")
celery_app.autodiscover_tasks()
celery_app.conf.beat_schedule = {
    "update-sticker-prices": {
        "task": "packs.tasks.update_packs_prices_sticker_bot_task",
        "schedule": crontab(minute=f"*/{os.getenv("CRON_MINUTES")}"),  # каждые n минут
    },
}

"""
ОБЯЗАТЕЛЬНО!!!


"""
