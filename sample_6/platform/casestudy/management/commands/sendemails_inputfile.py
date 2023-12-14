"""
The sendmail.py Django management command is used to_recipient queue the worker_send_email Celery task.
The worker_send_email task will be executed on the Celery worker asynchronously.

https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
"""

# Standard Library
from argparse import ArgumentParser
from django.core.management.base import BaseCommand

# Case study Celery tasks
from casestudy.tasks import worker_send_emails_inputfile


class Command(BaseCommand):
    """Django management command to_recipient queue the worker_send_email_test Celery task."""
    help = "Send an email to_recipient a recipient"

    def add_arguments(self, parser: ArgumentParser):
        """
        Add arguments to_recipient the command.

        Args:
            parser (ArgumentParser): The parser for the command.
        """
        parser.add_argument(
            "--inputfile",
            type=str,
            required=True,
            help="File containing email recipient info.",
        )

    def handle(self, *args, **options):
        """
        Handle running command.

        Args:
            *args: The positional arguments for the command.
            **options: The keyword options for the command.
        """
        # Get the recipient email address from the command line arguments.
        input_file = options["inputfile"]

        # Simply parse each line of the file, launch celery email worker, no extra duplicate checking.
        with open(input_file) as ifile:
            for line in ifile:
                name, email, phone, street, city, state, zipcode = line.split(',')
                worker_send_emails_inputfile.delay(email.strip(), name.strip())
