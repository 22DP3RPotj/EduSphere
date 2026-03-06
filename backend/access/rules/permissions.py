import rules
from enum import StrEnum
from backend.room.rules.predicates import is_participant, is_room_public
from backend.access.rules.predicates import can_manage_roles, has_higher_hierarchy


class AccessPermission(StrEnum):
    CREATE = "access.create"
    READ = "access.read"
    UPDATE = "access.update"
    DELETE = "access.delete"


rules.add_perm(AccessPermission.CREATE, can_manage_roles & has_higher_hierarchy)
rules.add_perm(AccessPermission.READ, is_room_public | is_participant)
rules.add_perm(AccessPermission.UPDATE, can_manage_roles & has_higher_hierarchy)
rules.add_perm(AccessPermission.DELETE, can_manage_roles & has_higher_hierarchy)
