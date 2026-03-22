import uuid
import pghistory
from typing import Optional, TYPE_CHECKING
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError

from backend.room.choices import VisibilityChoices
from backend.room.querysets import RoomQuerySet, TopicQuerySet

if TYPE_CHECKING:
    from backend.access.models import Role


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        app_label = "room"
        constraints = [
            models.CheckConstraint(
                condition=Q(name__regex=r"^[A-Za-z]+$"),
                name="letters_only_in_topic_name",
                violation_error_message="Topic name must consist of letters only.",
            ),
        ]
        indexes = [
            models.Index(fields=["name"]),
        ]
        ordering = [Lower("name").asc()]

    objects = TopicQuerySet.as_manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Room(models.Model):
    Visibility = VisibilityChoices

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_rooms"
    )
    default_role = models.ForeignKey(
        "access.Role",
        on_delete=models.SET_NULL,
        related_name="default_for_rooms",
        null=True,
        blank=True,
    )
    topics = models.ManyToManyField(Topic, related_name="rooms")
    visibility = models.CharField(
        max_length=16, choices=Visibility.choices, blank=True, default=Visibility.PUBLIC
    )
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="", max_length=512)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participants",
        through="access.Participant",
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RoomQuerySet.as_manager()

    class Meta:
        app_label = "room"
        ordering = ["-updated_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["host", "name"],
                name="unique_room_per_host",
                violation_error_message="You already have a room with this name.",
            ),
            models.CheckConstraint(
                condition=Q(name__regex=r"^[a-zA-Z0-9 ]+$"),
                name="valid_characters_in_room_name",
                violation_error_message="Room name can only contain letters, numbers and spaces.",
            ),
        ]
        indexes = [
            models.Index(fields=["updated_at"]),
        ]

    def update_visibility(self, new_visibility: VisibilityChoices):
        if self.visibility == new_visibility:
            return
        self.visibility = new_visibility
        self.save(update_fields=["visibility", "updated_at"])

    def update_default_role(self, new_default_role: "Optional[Role]"):
        if self.default_role == new_default_role:
            return
        self.default_role = new_default_role
        self.save(update_fields=["default_role_id", "updated_at"])

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.default_role_id and self.default_role.room_id != self.id:
            raise ValidationError(
                {"default_role": "Default role must belong to this room."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RoomHistory(
    pghistory.create_event_model(
        Room,
        fields=["name", "description", "visibility", "default_role"],
    )
):
    class Meta:
        app_label = "room"
