import uuid
import pghistory
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

from backend.account.models import User
from backend.core.constants import DELETED_USER
from backend.moderation.choices import ReportStatus, ACTIVE_STATUSES


class ReportReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=64, unique=True)
    label = models.CharField(max_length=128)
    allowed_content_types = models.ManyToManyField(
        ContentType,
        blank=True,
        related_name="report_reasons",
        help_text="Content types this reason applies to. Leave empty to allow for all targets.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "moderation"
        ordering = ["label"]

    def __str__(self):
        return self.label


class Report(models.Model):
    Status = ReportStatus

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    body = models.TextField(max_length=2048)
    reason = models.ForeignKey(
        ReportReason,
        on_delete=models.PROTECT,
        related_name="reports",
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PENDING
    )
    moderator_note = models.TextField(max_length=512, blank=True, default="")
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "moderation"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                condition=Q(status__in=ACTIVE_STATUSES),
                name="unique_active_report_per_user_target",
                violation_error_message="You already have an active report targeting this content.",
            )
        ]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["content_type", "object_id", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        username = self.user.username if self.user else DELETED_USER
        target = (
            str(self.content_object)
            if self.content_object
            else f"<{self.content_type}:{self.object_id}>"
        )
        return f"Report by {username} on {target}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def active_reports(cls, **filters):
        return cls.objects.filter(status__in=ACTIVE_STATUSES, **filters)

    @property
    def is_active_report(self):
        return self.status in ACTIVE_STATUSES


class ReportHistory(
    pghistory.create_event_model(
        Report,
        fields=["body", "reason", "status", "moderator_note", "moderator"],
    )
):
    class Meta:
        app_label = "moderation"
