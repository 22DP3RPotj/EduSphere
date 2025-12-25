import uuid
from django.db import models
from django.db.models.constraints import Q, CheckConstraint
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator, MaxLengthValidator

from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('lv', 'Latvian'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=32)
    bio = models.TextField(blank=True, default='', max_length=4096, validators=[MaxLengthValidator(4096)])
    avatar = models.ImageField(
        upload_to='avatars',
        blank=True, null=True,
        validators=[FileExtensionValidator(['svg','png','jpg','jpeg'])]
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en', blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.username = slugify(self.username)
        self.full_clean()
        super().save(*args, **kwargs)
    

class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = [Lower('name')]
        constraints = [
            CheckConstraint(
                condition=Q(name__regex=r'^[A-Za-z]+$'),
                name='no_spaces_in_topic',
                violation_error_message="Topic name must consist of letters only."),
        ]
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Room(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    topics = models.ManyToManyField(Topic, related_name='rooms')
    description = models.TextField(blank=True, default='', max_length=512, validators=[MaxLengthValidator(512)])
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
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
            models.Index(fields=['host', 'name']),
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
            'room': self.name,
        })

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField(max_length=2048, validators=[MaxLengthValidator(2048)])
    edited = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body

    class Meta:
        indexes = [
            models.Index(fields=['room', 'created']),
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
            'created': self.created.isoformat(),
            'edited': self.edited,
            'updated': self.updated.isoformat(),
            'userAvatar': self.user.avatar.name if self.user.avatar else None,
        }
        
    def update(self, body):
        if not self.edited:
            self.edited = True
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
    body = models.TextField(max_length=2048, validators=[MaxLengthValidator(2048)])
    reason = models.CharField(max_length=32, choices=ReportReason.choices)
    status = models.CharField(max_length=32, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    moderator_note = models.TextField(max_length=512, blank=True, default='', validators=[MaxLengthValidator(512)])
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
        return f"Report by {self.user.username} on {self.room.name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def active_reports(cls, **filters):
        return cls.objects.filter(status__in=cls.ACTIVE_STATUSES, **filters)

    @property
    def is_active_report(self):
        return self.status in self.ACTIVE_STATUSES
