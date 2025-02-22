import uuid
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class User(AbstractUser):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, default='')
    avatar = models.ImageField(
        upload_to='avatars',
        default='default.svg',
        validators=[FileExtensionValidator(allowed_extensions=['svg', 'png', 'jpg'])]
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.slug or self.username != User.objects.get(pk=self.pk).username:
            self.slug = slugify(self.username)
            while User.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:4]}"
        super().save(*args, **kwargs)
        
    class Meta:
        app_label = 'core'
    

class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    slug = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    description = models.TextField(blank=True, default='')
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
            )
        ]
        indexes = [
            models.Index(fields=['host', 'slug'])
        ]
        
    def save(self, *args, **kwargs):
        if not self.slug or self.name != Room.objects.get(pk=self.pk).name:
            self.slug = slugify(self.name)
            while Room.objects.filter(host=self.host, slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:4]}"
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('room', kwargs={
            'username': self.host.slug,
            'room': self.slug,
        })

class Message(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(self.body) > 50:
            return self.body[:50] + '...'
        return self.body

    class Meta:
        indexes = [
            models.Index(fields=['room', 'created']),  # Optimized queries for fetching room messages
            models.Index(fields=['user']),             # Optimized queries for fetching user messages
        ]
        ordering = ['-created']

    def serialize(self):
        """
        Serialize the message object for WebSocket or API responses.
        """
        return {
            'id': str(self.id),
            'user': self.user.username,
            'user_id': self.user.id,
            'room': str(self.room.id),
            'body': self.body,
            'created': self.created.isoformat(),
            'updated': self.updated.isoformat(),
        }
