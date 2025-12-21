import uuid
from django.db import models
from django.db.models.constraints import Q, CheckConstraint
from django.db.models.functions import Lower
from django.forms import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator, MaxValueValidator

from backend.core.enums import PermissionCode, RoleCode

from .managers import CustomUserManager


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

    objects = CustomUserManager()

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
        ordering = [Lower('username')]
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['date_joined'])
        ]
    

class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = [Lower('name')]
        indexes = [
            models.Index(fields=['name']),
        ]
        constraints = [
            CheckConstraint(
                condition=Q(name__regex=r'^[A-Za-z]+$'),
                name='letters_only_in_topic_name',
                violation_error_message="Topic name must consist of letters only."
            ),
        ]
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Room(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        PRIVATE = 'PRIVATE', 'Private'
        
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    default_role = models.ForeignKey("Role", on_delete=models.PROTECT, related_name='default_for_rooms')
    topics = models.ManyToManyField(Topic, related_name='rooms')
    visibility = models.CharField(max_length=16, choices=Visibility.choices, default=Visibility.PUBLIC, blank=True)
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    description = models.TextField(blank=True, default='', max_length=512)
    participants = models.ManyToManyField(User, related_name='participants', through="Participant", blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-updated', '-created']
        constraints = [
            models.UniqueConstraint(
                fields=['host', 'slug'],
                name='unique_room_per_host',
                violation_error_message='You already have a room with this name.'
            )
        ]
        indexes = [
            models.Index(fields=['updated']),
        ]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('room', kwargs={
            'username': self.host.username,
            'room': self.slug,
        })


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, choices=PermissionCode.choices, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.code
    
    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
        ]


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32, choices=RoleCode.choices)
    name = models.CharField(max_length=32)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='roles')
    description = models.TextField(max_length=512, blank=True, default='')
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)
    priority = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __str__(self):
        return self.name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'code'],
                name='unique_role_code_per_room'
            ),
            models.UniqueConstraint(
                fields=['room', 'name'],
                name='unique_role_name_per_room'
            ),
        ]
    

class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['room', 'joined_at']),
            models.Index(fields=['room', 'user']),
            models.Index(fields=['room', 'role']),
            models.Index(fields=['user', 'joined_at']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'room'], name='unique_participant'),
        ]
        ordering = ['-joined_at']
        
    def clean(self):
        if self.role.room_id != self.room_id:
            raise ValidationError("Role must belong to the same room as the participant.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} in {self.room.name}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField(max_length=2048)
    is_edited = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50] + ('...' if len(self.body) > 50 else '')

    class Meta:
        indexes = [
            models.Index(fields=['room', 'user', 'created']),
            models.Index(fields=['room', 'created']),
            models.Index(fields=['room', '-created']),
            models.Index(fields=['user', 'created']),
            models.Index(fields=['user']),
        ]
        ordering = ['-created']
        
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def serialize(self):
        return {
            'id': str(self.id),
            'user': self.user.username,
            'user_id': str(self.user.id),
            'body': self.body,
            'is_edited': self.is_edited,
            'created': self.created.isoformat(),
            'updated': self.updated.isoformat(),
            'user_avatar': self.user.avatar.name if self.user.avatar else None,
        }
        
    def update(self, body):
        if not self.is_edited:
            self.is_edited = True
        self.body = body
        self.save()
        

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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reports')
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
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'room'],
                condition=Q(status__in=['PENDING', 'UNDER_REVIEW']),
                name='unique_active_report_per_user_room',
                violation_error_message='You already have an active report targeting this room.'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'created']),
            models.Index(fields=['user', 'created']),
            models.Index(fields=['room', 'created']),
        ]
        ordering = ['-created']

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
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='invites')
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invites')
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=InviteStatus.choices, default=InviteStatus.PENDING)
    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
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
        ordering = ['-created']

    def __str__(self):
        return f"Invite of {self.invitee.username} to {self.room.name} by {self.inviter.username}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def active_invites(cls, **filters):
        return cls.objects.filter(status=cls.InviteStatus.PENDING, **filters)