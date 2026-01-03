from django.db import models


class RoleCode(models.TextChoices):
    OWNER = "owner", "Owner"
    MEMBER = "member", "Member"


class PermissionCode(models.TextChoices):
    ROOM_DELETE = "room.delete", "Delete room"
    ROOM_UPDATE = "room.update", "Update room"
    ROOM_MANAGE_VISIBILITY = "room.manage_visibility", "Manage room visibility"
    ROOM_SEND_INVITE = "room.invite", "Invite users"
    ROOM_KICK = "room.kick", "Remove users"
    ROOM_ROLE_MANAGE = "room.role_manage", "Manage roles"
    ROOM_DELETE_MESSAGE = "room.delete_message", "Delete message"
    ROOM_UPLOAD_FILE = "room.upload_file", "Allow file uploads"
