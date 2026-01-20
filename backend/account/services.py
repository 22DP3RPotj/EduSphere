from datetime import datetime
from typing import Optional
from django.core.exceptions import ValidationError
from django.db import transaction
from backend.account.models import User, UserBan


class RestrictionService:
    """Service class for managing user bans and restrictions."""

    @staticmethod
    def ban_user(
        user: User,
        banned_by: User,
        reason: str,
        expires_at: Optional[datetime] = None,
    ) -> UserBan:
        """
        Bans a user until the specified expiration date. Permanent if expires_at is None.

        Raises:
            ValidationError: If a user attempts to ban themselves.
        """
        if user == banned_by:
            raise ValidationError("Users cannot ban themselves.")

        with transaction.atomic():
            UserBan.objects.filter(user=user, is_active=True).update(is_active=False)

            ban = UserBan.objects.create(
                user=user,
                banned_by=banned_by,
                reason=reason,
                expires_at=expires_at,
                is_active=True,
            )

            user.is_active = False
            user.save(update_fields=["is_active"])

        return ban

    @staticmethod
    def unban_user(user: User) -> None:
        """
        Unbans a user, deactivating their bans and setting is_active to True.
        """
        with transaction.atomic():
            UserBan.objects.filter(user=user, is_active=True).update(is_active=False)

            user.is_active = True
            user.save(update_fields=["is_active"])

    @staticmethod
    def lift_ban(ban: UserBan) -> None:
        """
        Lifts a specific ban, deactivating it and reactivating the user if no other active bans exist.
        """
        with transaction.atomic():
            ban.is_active = False
            ban.save(update_fields=["is_active"])

            if not UserBan.objects.filter(user=ban.user, is_active=True).exists():
                ban.user.is_active = True
                ban.user.save(update_fields=["is_active"])

    @staticmethod
    def is_user_banned(user: User) -> bool:
        """
        Checks if a user is currently banned.

        Returns:
            bool: True if the user has an active ban, False otherwise.
        """
        return UserBan.objects.filter(user=user, is_active=True).exists()
