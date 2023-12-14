"""
Mail client for sending emails.

This client mocks interactions with an actual email service provider to_recipient simplify the
case studies dependencies. The client supports 2 methods 'send_email' and 'get_email_status'.
"""
from random import random, choices
from time import sleep
from uuid import uuid4
from django.core.cache import cache
from casestudy.models import Email


class EmailClient:
    """Mock email client for testing purposes."""

    class EmailStatus:
        """Status of an email."""

        # The email has been sent to_recipient the recipient, and the delivery status is still
        # unknown.
        SENT = "sent"

        # The email was attempted but was skipped due to duplicate task of overlapping recipient.
        SKIPPED = "skipped"

        # The email was successfully delivered to_recipient the recipient.
        DELIVERED = "delivered"

        # The email was not delivered to_recipient the recipient, and was bounced by the
        # recipient's email server. This failure is permanent and should not be retried.
        BOUNCED = "bounced"

        # The email was not delivered to_recipient the recipient, and was blocked by the
        # recipient's email server. This failure is not permanent and can be retried.
        BLOCKED = "blocked"

    def process(self, task_id: str, to_recipient: str, subject: str, body: str) -> Email:
        """
        Send an email asynchronously.

        This method returns immediately and does not wait for the email to_recipient be sent.
        In order to_recipient get the status of the email, use get_email_status.

        Parameters
        ----------
        task_id : current celery task id
        to_recipient : email recipient address
        subject : email subject
        body : email body

        Returns
        -------
        Email instance of varying statuses to be handled by launching task.
        """

        # set to_recipient level cache lock to ensure only one task in processing emails.
        recipient_lock = cache.add(f'{to_recipient}_lock', True, timeout=None)
        print(f'{to_recipient=}, {recipient_lock=}')

        if recipient_lock:
            try:
                # generate email only the first time.
                self.send_email(body=body,
                                subject=subject,
                                to_recipient=to_recipient,
                                task_id=task_id)
                saved_task_id, email = cache.get(to_recipient)
                # if this is non-original task targeting same recipient, just skip.
                if saved_task_id != task_id:
                    return Email(to_recipient=to_recipient,
                                 status=EmailClient.EmailStatus.SKIPPED)

                # get next email status if just sent or bounced.
                if email.status in [EmailClient.EmailStatus.SENT,
                                    EmailClient.EmailStatus.BOUNCED]:
                    email.status = self.next_status()

                cache.set(to_recipient, (saved_task_id, email), timeout=None)
                return email
            finally:
                # clear the recipient level lock upon completion.
                cache.delete(f'{to_recipient}_lock')
        else:
            # this happens only for duplicate task with recipient lock contention.
            return Email(to_recipient=to_recipient,
                         status=EmailClient.EmailStatus.SKIPPED)

    def send_email(self, task_id: str, to_recipient: str, subject: str, body: str) -> None:
        """
        Simulates email sending by
            1. generating email (only the first time)
            2. marking processing celery task id and newly created email instance.
        Only generates & marks email the first time, and subsequent calls don't have any effect.

        Parameters
        ----------
        task_id : processing celery task id
        to_recipient : email recipient address
        subject : email subject
        body : email body
        """

        saved_task_id, email = cache.get(to_recipient, default=(None, None))
        # create new email and save on the first time.
        if not email:
            print(f'Sending email: {to_recipient=} {subject=} {body=}')
            email = Email(eid=uuid4(),
                          body=body,
                          subject=subject,
                          to_recipient=to_recipient,
                          status=EmailClient.EmailStatus.SENT)
            # mark to_recipient -> processing id, email instance pair.
            cache.set(to_recipient, (task_id, email), timeout=None)

    def next_status(self) -> str:
        """
        Randomly generate next status of the email in transit.

        Returns
        -------
        One email status out of DELIVERED, BOUNCED, BLOCKED.
        """
        # ~10% of messages hold for a short time
        if random() < 0.1:
            sleep(1 + random() * 4)
        # Randomly select the email status.
        # ~80% of messages are delivered
        # ~10% of messages are bounced
        # ~10% of messages are blocked
        email_status = choices(
            [
                self.EmailStatus.DELIVERED,
                self.EmailStatus.BOUNCED,
                self.EmailStatus.BLOCKED,
            ],
            weights=[0.8, 0.1, 0.1],
        )[0]
        return email_status
