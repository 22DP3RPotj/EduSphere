import uuid

from django.db import models
from django.core.validators import MaxValueValidator
from django.forms import ValidationError

from backend.access.enums import PermissionCode


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, choices=PermissionCode.choices, unique=True, editable=False)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.code
    
    class Meta:
        app_label = 'access'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
        ]


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32)
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE, related_name='roles')
    description = models.TextField(max_length=512, blank=True, default='')
    priority = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'access'
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'name'],
                name='unique_role_name_per_room'
            ),
        ]


class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("account.User", on_delete=models.CASCADE)
    room = models.ForeignKey("room.Room", on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'access'
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
