import uuid
from django.db import models
from django.forms import ValidationError

from backend.messaging.choices import MessageStatusChoices


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    user = models.ForeignKey("account.User", on_delete=models.CASCADE)
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE)
    body = models.TextField(max_length=2048)
    is_edited = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50] + ('...' if len(self.body) > 50 else '')

    class Meta:
        app_label = 'messaging'
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


class MessageStatus(models.Model):
    Status = MessageStatusChoices
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey("account.User", on_delete=models.CASCADE, related_name='message_statuses')
    status = models.CharField(max_length=16, choices=Status.choices)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'messaging'
        indexes = [
            models.Index(fields=['message', 'user']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['message', 'user'], name='unique_message_status_per_user')
        ]
    
    def __str__(self):
        return f"Status of message {self.message.id} for user {self.user.username}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
