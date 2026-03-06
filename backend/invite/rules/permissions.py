import rules
from enum import StrEnum
from backend.invite.rules.predicates import (
    is_recipient,
    is_sender,
    can_manage_invite,
    can_manage_participants,
)


class InvitePermission(StrEnum):
    CREATE = "invite.create"
    READ = "invite.read"
    UPDATE = "invite.update"
    DELETE = "invite.delete"
    ACCEPT = "invite.accept"
    REJECT = "invite.reject"


rules.add_perm(InvitePermission.CREATE, can_manage_participants)
rules.add_perm(InvitePermission.READ, is_recipient | is_sender | can_manage_invite)
rules.add_perm(InvitePermission.UPDATE, can_manage_invite)
rules.add_perm(InvitePermission.DELETE, can_manage_invite)
rules.add_perm(InvitePermission.ACCEPT, is_recipient)
rules.add_perm(InvitePermission.REJECT, is_recipient)
