import uuid

import pghistory
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.db.models.functions import Lower
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import (
    FileExtensionValidator,
    MinLengthValidator,
    RegexValidator,
)

from backend.account.choices import EmailTypeChoices, UserStatusChoices, LanguageChoices
from backend.account.managers import UserManager
from backend.account.files.paths import avatar_upload_path
from backend.core.files.validators import FileSizeValidator, ImageValidator


class User(AbstractBaseUser, PermissionsMixin):
    Language = LanguageChoices
    Status = UserStatusChoices

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=32,
        unique=True,
        validators=[
            RegexValidator(
                r"^[-a-z0-9_]+$",
                "Username may only contain lowercase letters, digits, hyphens (-), and underscores (_).",
            ),
            MinLengthValidator(
                settings.MINIMAL_USERNAME_LENGTH,
                f"Username must be at least {settings.MINIMAL_USERNAME_LENGTH} characters long.",
            ),
        ],
    )
    name = models.CharField(max_length=32)
    bio = models.TextField(blank=True, default="", max_length=4096)
    language = models.CharField(
        choices=LanguageChoices.choices,
        blank=True,
        max_length=2,
        default=LanguageChoices.ENGLISH,
    )
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
    date_joined = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    verified_at = models.DateTimeField(null=True, blank=True)

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

    def verify(self):
        if not self.is_verified:
            self.verified_at = timezone.now()
            self.save(update_fields=["verified_at"])

    def update_password(self, new_password: str):
        self.set_password(new_password)
        self.save(update_fields=["password"])

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save(update_fields=["is_active"])

    def deactivate(self):
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active"])

    @property
    def is_verified(self):
        return self.verified_at is not None


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

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save(update_fields=["is_active"])

    def deactivate(self):
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active"])


class EmailToken(models.Model):
    Type = EmailTypeChoices

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_tokens"
    )
    type = models.CharField(max_length=32, choices=EmailTypeChoices.choices)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "account"
        indexes = [
            models.Index(fields=["user", "type"]),
        ]

    def __str__(self):
        return f"{self.type} token for {self.user.username}"

    def mark_as_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])


class UserHistory(
    pghistory.create_event_model(
        User,
        fields=["is_active", "is_staff", "is_superuser", "verified_at"],
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
