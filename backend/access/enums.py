from django.db import models


class RoleCode(models.TextChoices):
    OWNER = "owner", "Owner"
    MEMBER = "member", "Member"


class PermissionCode(models.TextChoices):
    ROOM_DELETE = "room.delete", "Delete room"
    ROOM_UPDATE = "room.update", "Update room"
    ROOM_MANAGE_VISIBILITY = "room.manage_visibility", "Manage room visibility"
    ROOM_MANAGE_PARTICIPANTS = (
        "room.manage_participants",
        "Invite or remove participants",
    )
    ROOM_MANAGE_ROLES = "room.manage_roles", "Manage roles"
    ROOM_DELETE_MESSAGE = "room.delete_message", "Delete message"
    ROOM_UPLOAD_FILE = "room.upload_file", "Allow file uploads"
