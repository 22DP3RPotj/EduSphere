from rules.predicates import predicate
from backend.access.enums import PermissionCode
from backend.access.models import Role
from backend.account.models import User
from backend.room.models import Room


@predicate
def can_manage_roles(user: User, role: Role) -> bool:
    from backend.access.services import RoleService

    return RoleService.has_permission(user, role.room, PermissionCode.ROOM_MANAGE_ROLES)


@predicate
def is_room_public(user: User, role: Role) -> bool:
    return role.room.visibility == Room.Visibility.PUBLIC


@predicate
def is_participant(user: User, role: Role) -> bool:
    return role.room.memberships.filter(user=user).exists()
