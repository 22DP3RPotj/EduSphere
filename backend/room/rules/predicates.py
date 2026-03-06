from rules.predicates import predicate
from backend.room.models import Room
from backend.account.models import User
from backend.access.services import RoleService
from backend.access.enums import PermissionCode


@predicate
def is_participant(user: User, room: Room) -> bool:
    return room.participants.filter(user=user).exists()


@predicate
def is_room_public(user: User, room: Room) -> bool:
    return room.visibility == Room.Visibility.PUBLIC


@predicate
def can_delete_room(user: User, room: Room) -> bool:
    return RoleService.has_permission(user, room, PermissionCode.ROOM_DELETE)


@predicate
def can_update_room(user: User, room: Room) -> bool:
    return RoleService.has_permission(user, room, PermissionCode.ROOM_UPDATE)
