import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(default='default.svg')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name[0:50]


class Room(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-updated', '-created']

class Message(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message by {self.user.username} in {self.room.name} at {self.created}'

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
            'created': self.created.strftime('%Y-%m-%d %H:%M:%S'),
            'updated': self.updated.strftime('%Y-%m-%d %H:%M:%S'),
        }
