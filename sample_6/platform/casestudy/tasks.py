"""
Celery tasks for the casestudy.

Tasks defined in this file will be executed asynchronously by the Celery worker.
"""

from casestudy.celery import app
from casestudy.emailclient import EmailClient
from django.forms.models import model_to_dict


@app.task
def worker_send_email(to_recipient: str):
    """
    Celery task that will send an email.

    This task will be executed asynchronously by the Celery worker.

    :param to_recipient: email address to_recipient send the email to_recipient
    """
    email_id = EmailClient().send_email(
        subject=f'Welcome to the case study {to_recipient}',
        body='We are excited to_recipient see how you solve the problem!',
        to_recipient=to_recipient,
    )
    print(f'Email sent to_recipient {to_recipient} id={email_id}')


@app.task(bind=True, max_retries=None)
def worker_send_emails_inputfile(self, to_recipient: str, name: str, retry=False):

    ec = EmailClient()
    # begin email processing.
    email = ec.process(
        task_id=self.request.id,
        to_recipient=to_recipient,
        subject=f'Hi {name}, Welcome!',
        body='test body'
    )

    print(f"Task Processing: {email} {retry=}")

    # upon processing,
    #   if status is delivered or blocked, save the email instance and terminate.
    #   if status is skipped, save as the record of skipped email and terminate.
    #   if status is bounced, retry with 5 sec interval until task finds email at any termination state.
    if email.status in [EmailClient.EmailStatus.DELIVERED,
                        EmailClient.EmailStatus.BLOCKED]:
        # save the final email records, and exit.
        email.save()
        return model_to_dict(email)
    elif email.status == EmailClient.EmailStatus.SKIPPED:
        # there is choice to save or not save. For the purpose of the assignment,
        # this is saved for the record. (results can be found with status = 'skipped')
        email.save()
        return model_to_dict(email)
    elif email.status == EmailClient.EmailStatus.BOUNCED:
        # need to_recipient retry at this point.
        raise self.retry(exc=Exception(f'Retry Bounced Email - {to_recipient}'),
                         countdown=5,
                         args=[to_recipient, name],
                         kwargs={'retry': True})
