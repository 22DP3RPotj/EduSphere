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
    PermissionCode.ROOM_SEND_INVITE: {
        "description": "Send and manage room invitations",
    },
    PermissionCode.ROOM_KICK: {
        "description": "Remove users from the room",
    },
    PermissionCode.ROOM_ROLE_MANAGE: {
        "description": "Manage room roles and permissions",
    },
    PermissionCode.ROOM_DELETE_MESSAGE: {
        "description": "Delete messages from the room",
    },
}

DEFAULT_ROLE_TEMPLATES: dict[RoleCode, RoleTemplate] = {
    RoleCode.OWNER: {
        "description": "Room owner",
        "permission_codes": list(PermissionCode.values),
        "priority": 100,
    },
    RoleCode.MEMBER: {
        "description": "Room member",
        "permission_codes": [],
        "priority": 0,
    },
}

