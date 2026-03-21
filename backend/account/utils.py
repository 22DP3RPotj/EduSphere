from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from backend.account.models import User


def get_inactivity_threshold() -> timedelta:
    return timedelta(seconds=settings.LAST_SEEN_INACTIVITY_THRESHOLD)


def update_last_seen(user) -> None:
    """Unconditionally update last_seen. Callers are responsible for throttling."""
    User.objects.filter(id=user.id).update(last_seen=now())
