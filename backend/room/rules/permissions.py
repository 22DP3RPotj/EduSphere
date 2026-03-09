import rules
from backend.room.rules.labels import RoomPermission
from backend.core.rules.predicates import is_authenticated
from backend.room.rules.predicates import (
    is_host,
    is_participant,
    is_room_public,
    can_delete_room,
    can_update_room,
    can_manage_participants,
)


rules.add_perm(RoomPermission.CREATE, is_authenticated)
rules.add_perm(RoomPermission.READ, is_room_public | is_participant)
rules.add_perm(RoomPermission.UPDATE, can_update_room)
rules.add_perm(RoomPermission.DELETE, can_delete_room)
rules.add_perm(RoomPermission.JOIN, is_authenticated & is_room_public)
rules.add_perm(RoomPermission.LEAVE, is_participant & ~is_host)
rules.add_perm(RoomPermission.MANAGE_PARTICIPANTS, can_manage_participants)
