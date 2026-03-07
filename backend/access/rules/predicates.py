from rules.predicates import predicate
from backend.access.enums import PermissionCode
from backend.access.models import Role
from backend.access.services import RoleService
from backend.account.models import User


@predicate
def can_manage_roles(user: User, role: Role) -> bool:
    return RoleService.has_permission(user, role.room, PermissionCode.ROOM_MANAGE_ROLES)


# TODO: Role may not yet be created to check
@predicate
def has_higher_hierarchy(user: User, role: Role) -> bool:
    participant = RoleService.get_participant(user, role.room)

    if not participant or not participant.role:
        return False

    return participant.role.priority > role.priority
