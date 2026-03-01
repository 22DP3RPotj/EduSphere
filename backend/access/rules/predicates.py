from rules.predicates import predicate
from backend.access.enums import PermissionCode
from backend.access.services import RoleService


@predicate
def is_self(user, participant):
    """Predicate that checks if the user is the same as the participant."""
    return user == participant.user


@predicate
def can_manage_roles(user, room):
    return RoleService.has_permission(user, room, PermissionCode.ROOM_MANAGE_ROLES)
