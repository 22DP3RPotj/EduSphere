from datetime import datetime
from typing import Optional

from django.db import transaction

from backend.account.models import User, UserBan


def ban_user(
    user: User,
    banned_by: User,
    reason: Optional[str],
    expires_at: Optional[datetime] = None,
) -> UserBan:
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


def unban_user(user: User) -> None:
    with transaction.atomic():
        UserBan.objects.filter(user=user, is_active=True).update(is_active=False)

        user.is_active = True
        user.save(update_fields=["is_active"])


def lift_ban(ban: UserBan) -> None:
    with transaction.atomic():
        ban.is_active = False
        ban.save(update_fields=["is_active"])

        if not UserBan.objects.filter(user=ban.user, is_active=True).exists():
            ban.user.is_active = True
            ban.user.save(update_fields=["is_active"])
