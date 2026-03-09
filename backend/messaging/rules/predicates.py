from rules.predicates import predicate
from backend.messaging.models import Message
from backend.account.models import User
from backend.access.services import RoleService
from backend.access.enums import PermissionCode
from backend.room.models import Room


@predicate
def is_author(user: User, message: Message) -> bool:
    return user == message.author


@predicate
def can_delete_message(user: User, message: Message) -> bool:
    return RoleService.has_permission(
        user, message.room, PermissionCode.ROOM_DELETE_MESSAGE
    )


@predicate
def is_participant(user: User, room: Room) -> bool:
    return room.memberships.filter(user=user).exists()
