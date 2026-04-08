from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from backend.account.models import User


def send_verification_email(user: User, token: str):
    if user.is_verified:
        return

    context = {
        "name": user.name,
        "verify_url": f"{settings.FRONTEND_URL}/verify-email?token={token}",
    }
    subject = "Verify your email"
    message = render_to_string("email/verify.txt", context)
    html_message = render_to_string("email/verify.html", context)

    send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_password_reset_email(user: User, token: str):
    if not user.is_active:
        return

    context = {
        "name": user.name,
        "reset_url": f"{settings.FRONTEND_URL}/reset-password?token={token}",
    }
    subject = "Reset your password"
    message = render_to_string("email/reset.txt", context)
    html_message = render_to_string("email/reset.html", context)

    send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
