import uuid

import pghistory
from django.conf import settings
from django.db import models
from django.db.models.functions import Lower
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import (
    FileExtensionValidator,
    MinLengthValidator,
    RegexValidator,
)

from backend.account.managers import UserManager
from backend.account.files.paths import avatar_upload_path
from backend.core.files.validators import FileSizeValidator, ImageValidator
from backend.core.constants import MINIMAL_USERNAME_LENGTH


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=32,
        unique=True,
        validators=[
            RegexValidator(
                r"^[-a-z0-9_]+$",
                "Username may only contain lowercase letters, digits, and -/_ characters.",
            ),
            MinLengthValidator(
                MINIMAL_USERNAME_LENGTH,
                f"Username must be at least {MINIMAL_USERNAME_LENGTH} characters long.",
            ),
        ],
    )
    name = models.CharField(max_length=32)
    bio = models.TextField(blank=True, default="", max_length=4096)
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["svg", "png", "jpg", "jpeg"]),
            ImageValidator(),
            FileSizeValidator(settings.MAX_FILE_SIZE_MB),
        ],
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username", "name"]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        app_label = "account"
        ordering = [Lower("username").asc()]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["date_joined"]),
        ]


class UserBan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bans",
    )
    banned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_bans",
    )
    reason = models.TextField(max_length=8192, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "account"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"Ban for {self.user.username}"


class UserHistory(
    pghistory.create_event_model(
        User,
        fields=["username", "email", "is_active", "is_staff", "is_superuser"],
    )
):
    class Meta:
        app_label = "account"


class UserBanHistory(
    pghistory.create_event_model(
        UserBan,
        fields=["user", "banned_by", "reason", "expires_at", "is_active"],
    )
):
    class Meta:
        app_label = "account"
