import uuid
from django.db import models
from django.db.models.constraints import Q, CheckConstraint
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.text import slugify

from backend.room.choices import Visibility


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'room'
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
    Visibility = Visibility
        
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    host = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name='hosted_rooms')
    default_role = models.ForeignKey("access.Role", on_delete=models.SET_NULL, related_name='default_for_rooms', null=True, blank=True)
    topics = models.ManyToManyField(Topic, related_name='rooms')
    visibility = models.CharField(max_length=16, choices=Visibility.choices, blank=True, default=Visibility.PUBLIC)
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    description = models.TextField(blank=True, default='', max_length=512)
    participants = models.ManyToManyField("core.User", related_name='participants', through="access.Participant", blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'room'
        ordering = ['-updated_at', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['host', 'slug'],
                name='unique_room_per_host',
                violation_error_message='You already have a room with this name.'
            )
        ]
        indexes = [
            models.Index(fields=['updated_at']),
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
