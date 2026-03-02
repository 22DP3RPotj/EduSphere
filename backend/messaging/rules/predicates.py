from rules.predicates import predicate
from backend.messaging.models import Message
from backend.account.models import User
from backend.access.services import RoleService
from backend.access.enums import PermissionCode


@predicate
def is_author(user: User, message: Message) -> bool:
    return user == message.author


@predicate
def can_delete_message(user: User, message: Message) -> bool:
    return RoleService.has_permission(
        user, message.room, PermissionCode.ROOM_DELETE_MESSAGE
    )
