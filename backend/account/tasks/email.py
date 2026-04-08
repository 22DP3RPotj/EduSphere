from enum import StrEnum
from celery import shared_task
from django.db import DatabaseError
from backend.account.email import send_password_reset_email, send_verification_email
from backend.account.models import User


class EmailType(StrEnum):
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"


@shared_task(
    autoretry_for=(DatabaseError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_verification_email_task(user: User):
    """
    Celery task for sending verification email.
    """
    return send_verification_email(user)


@shared_task(
    autoretry_for=(DatabaseError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_password_reset_email_task(user: User):
    """
    Celery task for sending password reset email.
    """
    return send_password_reset_email(user)


def enqueue_email(user: User, email_type: EmailType):
    """
    Helper function to enqueue email tasks.
    """
    match email_type:
        case EmailType.VERIFICATION:
            send_verification_email_task.delay(user=user)
        case EmailType.PASSWORD_RESET:
            send_password_reset_email_task.delay(user=user)
