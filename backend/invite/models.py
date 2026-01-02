import uuid
from django.db import models
from django.utils import timezone

from backend.invite.choices import InviteStatus


class Invite(models.Model):
    Status = InviteStatus
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE, related_name='invites')
    inviter = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name='sent_invites')
    invitee = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name='received_invites')
    role = models.ForeignKey("access.Role", on_delete=models.PROTECT)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        app_label = 'invite'
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'invitee'],
                name='unique_invite_per_user_room',
                violation_error_message='This user has already been invited to this room.'
            )
        ]
        indexes = [
            models.Index(fields=['room', 'invitee']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Invite of {self.invitee.username} to {self.room.name} by {self.inviter.username}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def active_invites(cls, **filters):
        return cls.objects.filter(status=cls.Status.PENDING, **filters)
    
    @property
    def is_expired(self) -> bool:
        """Check if invite has expired based on expires_at timestamp."""
        return timezone.now() > self.expires_at
    
    @property
    def is_resolved(self) -> bool:
        """Check if invite has been resolved (accepted or declined)"""
        return self.status in [
            self.Status.ACCEPTED,
            self.Status.DECLINED,
        ]
