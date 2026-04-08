from datetime import datetime
from typing import Optional

from backend.account.rules.labels import AccountPermission
from backend.core.exceptions import (
    PermissionException,
    ValidationException,
)
from backend.account import actions
from backend.account.models import User, UserBan


class AccountService:
    """Service for account mutation operations."""

    @staticmethod
    def register_user(
        *,
        username: str,
        name: str,
        email: str,
        password1: str,
        password2: str,
    ) -> User:
        """
        Register a new user and send a verification email.

        The user is created active — email verification is a feature-level
        gate (email_verified_at is None), not an auth-level one (is_active).

        Raises:
            FormValidationException: If form validation fails.
        """
        return actions.register_user(
            username=username,
            name=name,
            email=email,
            password1=password1,
            password2=password2,
        )

    @staticmethod
    def verify_email(*, token: str) -> User:
        """
        Mark the authenticated user's email as verified.

        Raises:
            ConflictException: If already verified.
        """
        return actions.verify_email(token=token)

    @staticmethod
    def resend_verification_email(*, user: User) -> None:
        """
        Re-send the verification email to the authenticated user.

        Raises:
            ConflictException: If already verified.
        """
        actions.resend_verification_email(user=user)

    @staticmethod
    def send_password_reset_email(*, email: str) -> None:
        """
        Send a password-reset email.
        Silent on unknown addresses to prevent enumeration.
        """
        actions.send_password_reset_email(email=email)

    @staticmethod
    def reset_password(*, token: str, new_password: str) -> User:
        """
        Reset a user's password using the uid + token from the reset email.

        Raises:
            ValidationException: If the link is invalid or expired.
        """
        return actions.reset_password(token=token, new_password=new_password)

    @staticmethod
    def change_password(*, user: User, old_password: str, new_password: str) -> User:
        """
        Change password for an authenticated user.

        Raises:
            ValidationException: If old_password is incorrect.
        """
        return actions.change_password(
            user=user,
            old_password=old_password,
            new_password=new_password,
        )


class ModerationService:
    """Service for superuser moderation operations."""

    @staticmethod
    def ban_user(
        *,
        user: User,
        banned_by: User,
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> UserBan:
        """
        Ban a user.

        Raises:
            PermissionException: If banned_by lacks ban permission.
        """
        if not banned_by.has_perm(AccountPermission.BAN):
            raise PermissionException("You do not have permission to ban users.")

        if user == banned_by:
            raise ValidationException("You cannot ban yourself.")

        return actions.ban_user(
            user=user,
            banned_by=banned_by,
            reason=reason,
            expires_at=expires_at,
        )

    @staticmethod
    def unban_user(*, actor: User, user: User) -> None:
        """
        Lift all active bans for a user.

        Raises:
            PermissionException: If actor lacks ban permission.
        """
        if not actor.has_perm(AccountPermission.BAN):
            raise PermissionException("You do not have permission to unban users.")

        actions.unban_user(user=user)

    @staticmethod
    def ban_users(
        *,
        actor: User,
        user_ids: list,
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> tuple[int, int]:
        """
        Ban a list of users. Skips already-banned users.

        Returns:
            (banned_count, skipped_count) tuple.

        Raises:
            PermissionException: If actor lacks ban permission.
        """
        if not actor.has_perm(AccountPermission.BAN):
            raise PermissionException("You do not have permission to ban users.")

        users = User.objects.filter(id__in=user_ids, is_active=True)

        banned = 0
        for user in users:
            if user == actor:
                continue  # Cannot ban yourself
            actions.ban_user(
                user=user,
                banned_by=actor,
                reason=reason,
                expires_at=expires_at,
            )
            banned += 1

        total = len(user_ids)
        skipped = total - banned
        return banned, skipped

    @staticmethod
    def unban_users(*, actor: User, user_ids: list) -> tuple[int, int]:
        """
        Lift all active bans for a list of users. Skips non-banned users.

        Returns:
            (unbanned_count, skipped_count) tuple.

        Raises:
            PermissionException: If actor lacks ban permission.
        """
        if not actor.has_perm(AccountPermission.BAN):
            raise PermissionException("You do not have permission to unban users.")

        users = User.objects.filter(id__in=user_ids, is_active=False)

        unbanned = 0
        for user in users:
            actions.unban_user(user=user)
            unbanned += 1

        total = len(user_ids)
        skipped = total - unbanned
        return unbanned, skipped

    @staticmethod
    def set_staff_status(*, actor: User, user_ids: list, is_staff: bool) -> int:
        """
        Bulk-update is_staff for a list of user PKs.

        Returns:
            Number of updated users.

        Raises:
            PermissionException: If actor lacks promote permission.
        """
        if not actor.has_perm(AccountPermission.PROMOTE):
            raise PermissionException(
                "You do not have permission to change staff status."
            )

        return User.objects.filter(id__in=user_ids).update(is_staff=is_staff)
