import uuid

import pghistory
from django.db import models
from django.conf import settings
from django.utils import timezone

from backend.invite.choices import InviteStatusChoices
from backend.invite.querysets import InviteQuerySet
from backend.invite.utils import generate_token, INVITE_TOKEN_LENGTH


class Invite(models.Model):
    Status = InviteStatusChoices

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    room = models.ForeignKey(
        "room.Room", on_delete=models.CASCADE, related_name="invites"
    )

    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invites"
    )

    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_invites",
    )

    role = models.ForeignKey(
        "access.Role", on_delete=models.SET_NULL, null=True, blank=True
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "invite"
        constraints = [
            models.UniqueConstraint(
                fields=["room", "invitee"],
                name="unique_invite_per_user_room",
                violation_error_message="This user has already been invited to this room.",
            )
        ]
        indexes = [
            models.Index(fields=["room", "invitee"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    objects = InviteQuerySet.as_manager()

    def __str__(self):
        return f"Invite of {self.invitee.username} to {self.room.name} by {self.inviter.username}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        """Check if invite has expired based on expires_at timestamp."""
        return self.expires_at is not None and self.expires_at < timezone.now()

    @property
    def is_resolved(self) -> bool:
        """Check if invite has been resolved."""
        return self.status in self.Status.resolved()

    @property
    def is_active(self) -> bool:
        """Check if invite is still active (pending and not expired)."""
        return self.status == self.Status.PENDING and not self.is_expired


class InviteLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(
        "room.Room", on_delete=models.CASCADE, related_name="invite_links"
    )
    role = models.ForeignKey(
        "access.Role", on_delete=models.SET_NULL, null=True, blank=True
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_invite_links",
    )

    is_active = models.BooleanField(default=True)

    max_uses = models.PositiveIntegerField(blank=True, null=True)
    uses = models.PositiveIntegerField(default=0)

    token = models.UUIDField(
        default=generate_token,
        max_length=INVITE_TOKEN_LENGTH,
        unique=True,
        editable=False,
    )
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "invite"
        indexes = [
            models.Index(fields=["room"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite link to {self.room.name} with role {self.role.name if self.role else 'None'}"


class InviteHistory(
    pghistory.create_event_model(
        Invite,
        fields=["status", "role"],
    )
):
    class Meta:
        app_label = "invite"
