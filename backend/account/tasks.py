from celery import shared_task
from django.utils import timezone
from django.db.utils import DatabaseError
from backend.account.models import UserBan
from backend.account.services import RestrictionService
import logging

logger = logging.getLogger(__name__)


def run_expire_user_bans():
    """
    Core logic for expring user bans.
    Separated from the task for easier testing and manual execution.
    """
    now = timezone.now()
    logger.info(f"Checking for expired user bans (time: {now})")

    expired_bans = UserBan.objects.filter(
        is_active=True, expires_at__lte=now
    ).select_related("user")

    count = 0
    for ban in expired_bans:
        RestrictionService.lift_ban(ban)
        count += 1

    if count > 0:
        logger.info(f"Expired {count} user bans.")

    return count


@shared_task(
    bind=True,
    autoretry_for=(DatabaseError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def expire_user_bans(self):
    """
    Celery task wrapper for checking expired user bans.
    """
    return run_expire_user_bans()
