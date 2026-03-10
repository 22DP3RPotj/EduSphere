from rules.predicates import predicate
from backend.access.enums import PermissionCode
from backend.invite.models import Invite
from backend.room.models import Room
from backend.account.models import User


@predicate
def is_sender(user: User, invite: Invite) -> bool:
    return invite.inviter == user


@predicate
def is_recipient(user: User, invite: Invite) -> bool:
    return invite.invitee == user


@predicate
def can_manage_invite(user: User, invite: Invite) -> bool:
    from backend.access.services import RoleService

    return RoleService.has_permission(
        user, invite.room, PermissionCode.ROOM_MANAGE_PARTICIPANTS
    )


@predicate
def can_manage_participants(user: User, room: Room) -> bool:
    from backend.access.services import RoleService

    return RoleService.has_permission(
        user, room, PermissionCode.ROOM_MANAGE_PARTICIPANTS
    )
