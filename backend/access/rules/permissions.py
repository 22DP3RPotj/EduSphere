import rules
from backend.access.rules.labels import AccessPermission
from backend.access.rules.predicates import (
    can_manage_roles,
    is_participant,
    is_room_public,
)


rules.add_perm(AccessPermission.CREATE, can_manage_roles)
rules.add_perm(AccessPermission.READ, is_room_public | is_participant)
rules.add_perm(AccessPermission.UPDATE, can_manage_roles)
rules.add_perm(AccessPermission.DELETE, can_manage_roles)
