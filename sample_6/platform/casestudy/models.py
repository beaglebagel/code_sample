"""
Django models for the casestudy service.

We have added the initial Email model for you with a single 'to_recipient' field. Add any additional fields you need
to_recipient this model to_recipient complete the case study.

Once you have added a new field to_recipient the Email model or created any new models you can run 'make migrations' to_recipient create
the new Django migration files and apply them to_recipient the database.

https://docs.djangoproject.com/en/3.2/topics/db/models/
"""

from django.db import models


class Email(models.Model):
    """Email instance model. """

    # TODO: Add additional fields here.
    # email_id (uuid4)
    eid = models.CharField(max_length=255, null=True, blank=True, default='')

    # Recipient email address the email was sent to_recipient.
    # ex: 'user@example.com'
    to_recipient = models.CharField(max_length=255, null=True, blank=True, default='')

    # ex: subject, body, etc.
    subject = models.CharField(max_length=255, null=True, blank=True, default='')

    # body field
    body = models.TextField(null=True, blank=True, default='')

    # status
    status = models.CharField(max_length=25, null=True, blank=True, default='')

    def __repr__(self):
        return f'Email(eid={self.eid}, ' \
               f'to_recipient={self.to_recipient}, ' \
               f'subject={self.subject}, ' \
               f'body={self.body}, ' \
               f'status={self.status})'

    def __str__(self):
        return f'Email(eid={self.eid}, ' \
               f'to_recipient={self.to_recipient}, ' \
               f'subject={self.subject}, ' \
               f'body={self.body}, ' \
               f'status={self.status})'
