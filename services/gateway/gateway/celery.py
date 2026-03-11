import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gateway.settings.development")

app = Celery("gateway")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
