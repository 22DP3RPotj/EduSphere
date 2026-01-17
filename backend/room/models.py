import uuid
import pghistory
from django.conf import settings
from django.db import models
from django.db.models import Q, CheckConstraint
from django.db.models.functions import Lower

from backend.room.choices import RoomVisibility


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "room"
        ordering = [Lower("name").asc()]
        indexes = [
            models.Index(fields=["name"]),
        ]
        constraints = [
            CheckConstraint(
                condition=Q(name__regex=r"^[A-Za-z]+$"),
                name="letters_only_in_topic_name",
                violation_error_message="Topic name must consist of letters only.",
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Room(models.Model):
    Visibility = RoomVisibility

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

    def __str__(self):
        return self.name

    class Meta:
        app_label = "room"
        ordering = ["-updated_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["host", "name"],
                name="unique_room_per_host",
                violation_error_message="You already have a room with this name.",
            )
        ]
        indexes = [
            models.Index(fields=["updated_at"]),
        ]

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
