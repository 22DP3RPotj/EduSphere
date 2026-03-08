from datetime import datetime
from typing import Optional

from django.core.exceptions import ValidationError

from backend.account import actions
from backend.account.models import User, UserBan


class RestrictionService:
    """Service class for managing user bans and restrictions."""

    @staticmethod
    def ban_user(
        user: User,
        banned_by: User,
        reason: Optional[str],
        expires_at: Optional[datetime] = None,
    ) -> UserBan:
        """
        Bans a user until the specified expiration date. Permanent if expires_at is None.

        Raises:
            ValidationError: If a user attempts to ban themselves.
        """
        if user == banned_by:
            raise ValidationError("Users cannot ban themselves.")

        return actions.ban_user(
            user=user,
            banned_by=banned_by,
            reason=reason,
            expires_at=expires_at,
        )

    @staticmethod
    def unban_user(user: User) -> None:
        """
        Unbans a user, deactivating their bans and setting is_active to True.
        """
        actions.unban_user(user=user)

    @staticmethod
    def lift_ban(ban: UserBan) -> None:
        """
        Lifts a specific ban, deactivating it and reactivating the user if no other active bans exist.
        """
        actions.lift_ban(ban=ban)

    @staticmethod
    def is_user_banned(user: User) -> bool:
        """
        Checks if a user is currently banned.

        Returns:
            bool: True if the user has an active ban, False otherwise.
        """
        return UserBan.objects.filter(user=user, is_active=True).exists()
