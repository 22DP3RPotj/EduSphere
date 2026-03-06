import uuid
import pghistory
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

from backend.account.models import User
from backend.core.constants import DELETED_USER
from backend.moderation.choices import (
    ActionPriorityChoices,
    CaseStatusChoices,
    ActionChoices,
)


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(
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
    description = models.TextField(max_length=2048, blank=True, default="")
    reason = models.ForeignKey(
        ReportReason,
        on_delete=models.PROTECT,
        related_name="reports",
    )

    case = models.ForeignKey(
        "ModerationCase",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reports",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "moderation"
        indexes = [
            models.Index(fields=["case", "created_at"]),
            models.Index(fields=["reporter", "created_at"]),
            models.Index(fields=["content_type", "object_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["reporter", "content_type", "object_id"],
                condition=Q(reporter__isnull=False),
                name="unique_report_per_reporter_per_target",
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        username = self.reporter.username if self.reporter else DELETED_USER
        target = (
            str(self.content_object)
            if self.content_object
            else f"<{self.content_type}:{self.object_id}>"
        )
        return f"Report by {username} on {target}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ModerationCase(models.Model):
    Status = CaseStatusChoices
    ActionPriority = ActionPriorityChoices

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="moderation_cases",
    )
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PENDING
    )

    priority = models.IntegerField(
        choices=ActionPriority.choices, default=ActionPriority.LOW
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "moderation"
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id"],
                condition=Q(status__in=CaseStatusChoices.active()),
                name="unique_active_case_per_target",
            )
        ]
        indexes = [
            models.Index(fields=["status", "priority", "created_at"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        target = (
            str(self.content_object)
            if self.content_object
            else f"<{self.content_type}:{self.object_id}>"
        )
        return f"Case for {target} - Status: {self.status}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ModerationAction(models.Model):
    Action = ActionChoices

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(
        ModerationCase,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderation_actions",
    )
    action = models.CharField(max_length=32, choices=Action.choices)
    note = models.TextField(max_length=512, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "moderation"
        ordering = ["created_at"]

    def __str__(self):
        moderator_name = self.moderator.username if self.moderator else DELETED_USER
        return f"Action: {self.action} by {moderator_name} on case {self.case_id}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ReportHistory(
    pghistory.create_event_model(
        Report,
        fields=["description", "reason", "case"],
    )
):
    class Meta:
        app_label = "moderation"


class ModerationCaseHistory(
    pghistory.create_event_model(
        ModerationCase,
        fields=["status", "priority"],
    )
):
    class Meta:
        app_label = "moderation"


class ModerationActionHistory(
    pghistory.create_event_model(
        ModerationAction,
        fields=["action", "note", "moderator"],
    )
):
    class Meta:
        app_label = "moderation"
