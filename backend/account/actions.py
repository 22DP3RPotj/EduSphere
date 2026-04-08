from typing import Optional
from datetime import datetime

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from backend.account.models import User, UserBan
from backend.core.exceptions import (
    ConflictException,
    ValidationException,
    FormValidationException,
)
from backend.account.forms import RegisterForm
from backend.account.tasks.email import enqueue_email, EmailType


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

        transaction.on_commit(lambda: enqueue_email(user, EmailType.VERIFICATION))

    return user


def verify_email(*, user: User) -> User:
    if user.is_verified:
        raise ConflictException("Account is already verified.")

    user.verified_at = timezone.now()
    user.save(update_fields=["verified_at"])

    return user


def resend_verification_email(*, user: User) -> None:
    if user.is_verified:
        raise ConflictException("Account is already verified.")

    transaction.on_commit(lambda: enqueue_email(user, EmailType.VERIFICATION))


def send_password_reset_email(*, email: str) -> None:
    """Silent on failure to prevent email enumeration."""
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return

    transaction.on_commit(lambda: enqueue_email(user, EmailType.PASSWORD_RESET))


def reset_password(*, uid: str, token: str, new_password: str) -> User:
    try:
        pk = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=pk, is_active=True)
    except (User.DoesNotExist, ValueError, TypeError):
        raise ValidationException("Invalid password reset link.")

    if not default_token_generator.check_token(user, token):
        raise ValidationException("Password reset link is invalid or has expired.")

    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        raise ValidationException("\n".join(e.messages))

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return user


def change_password(*, user: User, old_password: str, new_password: str) -> User:
    if not user.check_password(old_password):
        raise ValidationException("Current password is incorrect.")

    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        raise ValidationException("\n".join(e.messages))

    user.set_password(new_password)
    user.save(update_fields=["password"])

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
        user.is_active = False
        user.save(update_fields=["is_active"])

    return ban


def unban_user(*, user: User) -> User:
    with transaction.atomic():
        UserBan.objects.filter(user=user, is_active=True).update(is_active=False)
        user.is_active = True
        user.save(update_fields=["is_active"])

    return user


def lift_ban(*, ban: UserBan) -> None:
    with transaction.atomic():
        ban.is_active = False
        ban.save(update_fields=["is_active"])

        if not UserBan.objects.filter(user=ban.user, is_active=True).exists():
            ban.user.is_active = True
            ban.user.save(update_fields=["is_active"])


def is_user_banned(user: User) -> bool:
    return (
        UserBan.objects.filter(
            user=user,
            is_active=True,
        )
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
        .exists()
    )
