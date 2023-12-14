"""
The sendmail.py Django management command is used to_recipient queue the worker_send_email Celery task.
The worker_send_email task will be executed on the Celery worker asynchronously.

https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
"""

# Standard Library
from argparse import ArgumentParser
from django.core.management.base import BaseCommand

# Case study Celery tasks
from casestudy.tasks import worker_send_email


class Command(BaseCommand):
    """Django management command to_recipient queue the worker_send_email Celery task."""
    help = "Send an email to_recipient a recipient"

    def add_arguments(self, parser: ArgumentParser):
        """
        Add arguments to_recipient the command.

        Args:
            parser (ArgumentParser): The parser for the command.
        """
        parser.add_argument(
            "--count",
            type=int,
            required=True,
            help="Count of emails to_recipient send",
        )

    def handle(self, *args, **options):
        """
        Handle running command.

        Args:
            *args: The positional arguments for the command.
            **options: The keyword options for the command.
        """
        # Get the recipient email address from the command line arguments.
        count = options.get("count")

        # Queue the worker_send_email task that will execute on the Celery worker.
        for i in range(count):
            worker_send_email.delay(f'user_{i}@example.com')


