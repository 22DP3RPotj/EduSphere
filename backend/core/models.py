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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, default='', validators=[MaxLengthValidator(500)])
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
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.username = slugify(self.username)
        self.full_clean()
        super().save(*args, **kwargs)
    

class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = [Lower('name')]
        constraints = [
            CheckConstraint(
                check=Q(name__regex=r'^[A-Za-z]+$'),
                name='no_spaces_in_topic',
                violation_error_message="Topic name must consist of letters only."),
        ]
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Room(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    description = models.TextField(blank=True, default='', validators=[MaxLengthValidator(500)])
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-updated', '-created']
        constraints = [
            models.UniqueConstraint(
                fields=['host', 'name'],
                name='unique_room_per_host',
                violation_error_message='You already have a room with this name.'
            )
        ]
        indexes = [
            models.Index(fields=['host', 'name']),
            models.Index(fields=['topic']),
            models.Index(fields=['updated']),
        ]
        
    def save(self, *args, **kwargs):
        if not self.slug or self.name != Room.objects.get(pk=self.pk).name:
            base_slug = slugify(self.name)
            self.slug = base_slug
            while Room.objects.filter(host=self.host, slug=self.slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
        self.full_clean()
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('room', kwargs={
            'username': self.host.username,
            'room': self.name,
        })

class Message(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField(max_length=500, validators=[MaxLengthValidator(500)])
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
        """
        Serialize the message object for WebSocket or API responses.
        """
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
        """
        Update the message body and save it to the database.
        """
        self.body = body
        self.edited = True
        self.save()
        