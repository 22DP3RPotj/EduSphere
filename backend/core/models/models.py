import uuid
from django.db import models
from django.db.models.constraints import Q, CheckConstraint
from django.db.models.functions import Lower
from django.forms import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=32)
    bio = models.TextField(blank=True, default='', max_length=4096)
    avatar = models.ImageField(
        upload_to='avatars',
        blank=True, null=True,
        validators=[FileExtensionValidator(['svg','png','jpg','jpeg'])]
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.username = slugify(self.username)
        self.full_clean()
        super().save(*args, **kwargs)
        
    class Meta:
        app_label = 'core'
        ordering = [Lower('username')]
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['date_joined'])
        ]
    

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE)
    body = models.TextField(max_length=2048)
    is_edited = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50] + ('...' if len(self.body) > 50 else '')

    class Meta:
        app_label = 'core'
        indexes = [
            models.Index(fields=['room', 'user', 'created_at']),
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user']),
        ]
        ordering = ['-created_at']
    
    def clean(self):
        if self.parent and self.parent.room_id != self.room_id:
            raise ValidationError("Parent message must be in the same room as the message.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


        

class Report(models.Model):
    class ReportStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        RESOLVED = 'RESOLVED', 'Resolved'
        DISMISSED = 'DISMISSED', 'Dismissed'

    class ReportReason(models.TextChoices):
        SPAM = 'SPAM', 'Spam'
        HARASSMENT = 'HARASSMENT', 'Harassment'
        INAPPROPRIATE_CONTENT = 'INAPPROPRIATE_CONTENT', 'Inappropriate Content'
        HATE_SPEECH = 'HATE_SPEECH', 'Hate Speech'
        OTHER = 'OTHER', 'Other'
        
    ACTIVE_STATUSES = (
        ReportStatus.PENDING,
        ReportStatus.UNDER_REVIEW,
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("core.User", on_delete=models.SET_NULL, null=True, related_name='reports')
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE, related_name='reports')
    body = models.TextField(max_length=2048)
    reason = models.CharField(max_length=32, choices=ReportReason.choices)
    status = models.CharField(max_length=32, choices=ReportStatus.choices, default=ReportStatus.PENDING)
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
        app_label = 'core'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'room'],
                condition=Q(status__in=['PENDING', 'UNDER_REVIEW']),
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
        return cls.objects.filter(status__in=cls.ACTIVE_STATUSES, **filters)

    @property
    def is_active_report(self):
        return self.status in self.ACTIVE_STATUSES


class Invite(models.Model):
    class InviteStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'
        EXPIRED = 'EXPIRED', 'Expired'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE, related_name='invites')
    inviter = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name='sent_invites')
    invitee = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name='received_invites')
    role = models.ForeignKey("access.Role", on_delete=models.PROTECT)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=InviteStatus.choices, default=InviteStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        app_label = 'core'
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
        return cls.objects.filter(status=cls.InviteStatus.PENDING, **filters)
    
    @property
    def is_expired(self) -> bool:
        """Check if invite has expired based on expires_at timestamp."""
        return timezone.now() > self.expires_at