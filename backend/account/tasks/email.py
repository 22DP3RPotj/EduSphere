from uuid import UUID

from celery import shared_task
from django.db import DatabaseError
from backend.account.choices import EmailTypeChoices
from backend.account.email import send_password_reset_email, send_verification_email
from backend.account.models import User


@shared_task(
    autoretry_for=(DatabaseError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_verification_email_task(user_id: UUID, token: str):
    """
    Celery task for sending verification email.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    return send_verification_email(user, token)


@shared_task(
    autoretry_for=(DatabaseError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_password_reset_email_task(user_id: UUID, token: str):
    """
    Celery task for sending password reset email.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    return send_password_reset_email(user, token)


def enqueue_email(user_id: UUID, email_type: EmailTypeChoices, token: str):
    """
    Helper function to enqueue email tasks.
    """
    match email_type:
        case EmailTypeChoices.VERIFICATION:
            send_verification_email_task.delay(user_id=user_id, token=token)
        case EmailTypeChoices.PASSWORD_RESET:
            send_password_reset_email_task.delay(user_id=user_id, token=token)
