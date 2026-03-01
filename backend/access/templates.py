from typing import TypedDict

from backend.access.enums import PermissionCode, RoleCode


class PermissionTemplate(TypedDict):
    description: str


class RoleTemplate(TypedDict):
    description: str
    permission_codes: list[str]
    priority: int


PERMISSION_TEMPLATES: dict[PermissionCode, PermissionTemplate] = {
    PermissionCode.ROOM_DELETE: {
        "description": "Delete room",
    },
    PermissionCode.ROOM_UPDATE: {
        "description": "Update room settings",
    },
    PermissionCode.ROOM_MANAGE_VISIBILITY: {
        "description": "Manage room visibility settings",
    },
    PermissionCode.ROOM_MANAGE_PARTICIPANTS: {
        "description": "Invite or remove participants",
    },
    PermissionCode.ROOM_MANAGE_ROLES: {
        "description": "Manage room roles and permissions",
    },
    PermissionCode.ROOM_DELETE_MESSAGE: {
        "description": "Delete messages from the room",
    },
    PermissionCode.ROOM_UPLOAD_FILE: {
        "description": "Allow file uploads",
    },
}

DEFAULT_ROLE_TEMPLATES: dict[RoleCode, RoleTemplate] = {
    RoleCode.OWNER: {
        "description": "Room owner",
        "permission_codes": PermissionCode.values,
        "priority": 100,
    },
    RoleCode.MEMBER: {
        "description": "Room member",
        "permission_codes": [],
        "priority": 0,
    },
}
