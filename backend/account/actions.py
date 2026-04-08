import secrets
from typing import Optional
from datetime import datetime, timedelta

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from backend.account.choices import EmailTypeChoices
from backend.account.models import EmailToken, User, UserBan
from backend.core.exceptions import (
    ConflictException,
    ValidationException,
    FormValidationException,
)
from backend.account.forms import RegisterForm
from backend.account.tasks.email import enqueue_email


TOKEN_EXPIRY = {
    EmailTypeChoices.VERIFICATION: timedelta(days=3),
    EmailTypeChoices.PASSWORD_RESET: timedelta(hours=1),
}


def _create_email_token(user: User, token_type: EmailTypeChoices) -> EmailToken:
    # Invalidate any prior unused tokens of this type
    EmailToken.objects.filter(user=user, type=token_type, used_at__isnull=True).delete()

    return EmailToken.objects.create(
        user=user,
        type=token_type,
        token=secrets.token_urlsafe(32),
        expires_at=timezone.now() + TOKEN_EXPIRY[token_type],
    )


def register_user(
    *,
    username: str,
    name: str,
    email: str,
    password1: str,
    password2: str,
) -> User:
    form = RegisterForm(
        {
            "username": username,
            "name": name,
            "email": email,
            "password1": password1,
            "password2": password2,
        }
    )

    if not form.is_valid():
        raise FormValidationException("Invalid registration data", errors=form.errors)

    with transaction.atomic():
        user: User = form.save()

        email_token = _create_email_token(user, EmailTypeChoices.VERIFICATION)
        transaction.on_commit(
            lambda: enqueue_email(
                user.id, EmailTypeChoices.VERIFICATION, email_token.token
            )
        )

    return user


def verify_email(*, token: str) -> User:
    try:
        email_token = EmailToken.objects.select_related("user").get(
            token=token,
            type=EmailTypeChoices.VERIFICATION,
            used_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
    except EmailToken.DoesNotExist:
        raise ValidationException("Invalid or expired verification link.")

    user = email_token.user
    if user.is_verified:
        email_token.mark_as_used()
        raise ConflictException("Account is already verified.")

    with transaction.atomic():
        user.verify()
        email_token.mark_as_used()

    return user


def resend_verification_email(*, user: User) -> None:
    if user.is_verified:
        raise ConflictException("Account is already verified.")

    with transaction.atomic():
        email_token = _create_email_token(user, EmailTypeChoices.VERIFICATION)
        transaction.on_commit(
            lambda: enqueue_email(
                user.id, EmailTypeChoices.VERIFICATION, email_token.token
            )
        )


def send_password_reset_email(*, email: str) -> None:
    """Silent on failure to prevent email enumeration."""
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return

    with transaction.atomic():
        email_token = _create_email_token(user, EmailTypeChoices.PASSWORD_RESET)
        transaction.on_commit(
            lambda: enqueue_email(
                user.id, EmailTypeChoices.PASSWORD_RESET, email_token.token
            )
        )


def reset_password(*, token: str, new_password: str) -> User:
    try:
        email_token = EmailToken.objects.select_related("user").get(
            token=token,
            type=EmailTypeChoices.PASSWORD_RESET,
            used_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
    except (EmailToken.DoesNotExist, ValueError, TypeError):
        raise ValidationException("Invalid password reset link.")

    user = email_token.user

    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        raise ValidationException("\n".join(e.messages))

    with transaction.atomic():
        user.update_password(new_password)
        email_token.mark_as_used()

    return user


def change_password(*, user: User, old_password: str, new_password: str) -> User:
    if not user.check_password(old_password):
        raise ValidationException("Current password is incorrect.")

    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        raise ValidationException("\n".join(e.messages))

    user.update_password(new_password)

    return user


def ban_user(
    *,
    user: User,
    banned_by: Optional[User] = None,
    reason: Optional[str] = None,
    expires_at: Optional[datetime] = None,
) -> UserBan:
    with transaction.atomic():
        ban = UserBan.objects.create(
            user=user,
            banned_by=banned_by,
            reason=reason or "",
            expires_at=expires_at,
            is_active=True,
        )
        user.deactivate()

    return ban


def unban_user(*, user: User) -> User:
    with transaction.atomic():
        UserBan.objects.filter(user=user, is_active=True).update(is_active=False)
        user.activate()

    return user


def lift_ban(*, ban: UserBan) -> None:
    with transaction.atomic():
        ban.deactivate()

        if not UserBan.objects.filter(user=ban.user, is_active=True).exists():
            ban.user.activate()


def is_user_banned(user: User) -> bool:
    return (
        UserBan.objects.filter(
            user=user,
            is_active=True,
        )
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
        .exists()
    )
