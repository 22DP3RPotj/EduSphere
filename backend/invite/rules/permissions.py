import rules
from backend.invite.rules.labels import InvitePermission
from backend.invite.rules.predicates import (
    is_recipient,
    is_sender,
    can_manage_invite,
    can_manage_participants,
)


rules.add_perm(InvitePermission.CREATE, can_manage_participants)
rules.add_perm(InvitePermission.VIEW, is_recipient | is_sender | can_manage_invite)
rules.add_perm(InvitePermission.UPDATE, can_manage_invite)
rules.add_perm(InvitePermission.DELETE, can_manage_invite)
rules.add_perm(InvitePermission.ACCEPT, is_recipient)
rules.add_perm(InvitePermission.REJECT, is_recipient)
