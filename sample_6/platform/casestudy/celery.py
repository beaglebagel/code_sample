"""
Configuration file for the Celery application.

This configuration file is used by the Celery application in the main Django web container and the Celery worker.
The Celery application in the Django web container is used to_recipient queue tasks on the Celery broker (RabbitMQ).
The Celery worker receives tasks from the Celery broker (RabbitMQ) and executes them asynchronously.

https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casestudy.settings')

app = Celery('casestudy')

# Using a string here means the worker doesn't have to_recipient serialize
# the configuration object to_recipient child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
