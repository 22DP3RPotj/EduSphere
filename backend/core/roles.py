from django.db import transaction

from .enums import PermissionCode, RoleCode
from .models import Role, Permission, Room


ROLE_TEMPLATES = {
    RoleCode.OWNER: {
        "description": "Room owner",
        "permissions": PermissionCode.values,
    },
    RoleCode.MEMBER: {
        "description": "Room member",
        "permissions": [],
    },
}


def create_default_roles(room: Room):
    with transaction.atomic():
        for role_code, data in ROLE_TEMPLATES.items():
            role = Role.objects.create(
                room=room,
                name=role_code.label,
                description=data["description"],
            )
            perms = Permission.objects.filter(
                code__in=[p.value for p in data["permissions"]]
            )
            role.permissions.set(perms)