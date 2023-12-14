"""
Module for the casestudy Django app.

https://docs.djangoproject.com/en/4.2/ref/applications/
"""

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html

from casestudy.celery import app as celery_app
__all__ = ('celery_app',)