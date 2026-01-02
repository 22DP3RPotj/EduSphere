import uuid
from django.db import models
from django.db.models.functions import Lower
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator

from backend.account.managers import UserManager


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
        app_label = 'account'
        ordering = [Lower('username')]
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['date_joined'])
        ]
