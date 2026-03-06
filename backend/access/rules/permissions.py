import rules
from enum import StrEnum
from backend.core.rules.predicates import is_authenticated
from backend.room.rules.predicates import is_participant, is_room_public, can_delete_room, can_update_room
from backend.access.rules.predicates import can_manage_roles, has_higher_hierarchy

class AccessPermission(StrEnum):
    CREATE = "room.create"
    READ = "room.read"
    UPDATE = "room.update"
    DELETE = "room.delete"


rules.add_perm(AccessPermission.CREATE, can_manage_roles & has_higher_hierarchy)
rules.add_perm(AccessPermission.READ, is_room_public | is_participant)
rules.add_perm(AccessPermission.UPDATE, can_update_room)
rules.add_perm(AccessPermission.DELETE, can_delete_room)
