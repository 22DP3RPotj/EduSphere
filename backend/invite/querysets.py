from typing import TYPE_CHECKING, Self

from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from backend.invite.models import Invite  # noqa: F401


class InviteQuerySet(models.QuerySet["Invite"]):
    """Custom QuerySet for Invite model."""

    def pending(self) -> Self:
        return self.filter(status=self.model.Status.PENDING)

    def expired(self) -> Self:
        return self.filter(status=self.model.Status.EXPIRED)

    def active(self) -> Self:
        now = timezone.now()

        return self.filter(status=self.model.Status.PENDING).exclude(expires_at__lt=now)

    def refresh(self) -> Self:
        """Refresh invite statuses based on current time."""
        now = timezone.now()
        self.filter(status=self.model.Status.PENDING, expires_at__lt=now).update(
            status=self.model.Status.EXPIRED
        )
        return self.filter(status=self.model.Status.PENDING).exclude(expires_at__lt=now)
