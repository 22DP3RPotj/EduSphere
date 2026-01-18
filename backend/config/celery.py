import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

app = Celery("backend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
