import rules
from enum import StrEnum
from backend.access.rules.predicates import is_self, can_manage_roles


class RoomPermission(StrEnum):
    CHANGE_ROLE = "access.change_role"


rules.add_perm(RoomPermission.CHANGE_ROLE, is_self | can_manage_roles)
