import uuid
from django.db import models
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
