import uuid
from django.db import models
from django.db.models import Q

from backend.account.models import User
from backend.moderation.choices import ReportReason, ReportStatus, ACTIVE_STATUSES


class Report(models.Model):
    Reason = ReportReason
    Status = ReportStatus
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True, related_name='reports')
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE, related_name='reports')
    body = models.TextField(max_length=2048)
    reason = models.CharField(max_length=32, choices=Reason.choices)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    moderator_note = models.TextField(max_length=512, blank=True, default='')
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'moderation'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'room'],
                condition=Q(status__in=ACTIVE_STATUSES),
                name='unique_active_report_per_user_room',
                violation_error_message='You already have an active report targeting this room.'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['room', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else "<Deleted user>"
        return f"Report by {username} on {self.room.name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def active_reports(cls, **filters):
        return cls.objects.filter(status__in=ACTIVE_STATUSES, **filters)

    @property
    def is_active_report(self):
        return self.status in ACTIVE_STATUSES

