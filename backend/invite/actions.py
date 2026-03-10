from datetime import datetime
from typing import Optional

from django.db import IntegrityError, transaction

from backend.access.models import Role
from backend.account.models import User
from backend.core.exceptions import (
    ConflictException,
    FormValidationException,
)
from backend.invite.forms import InviteForm
from backend.invite.models import Invite
from backend.access.models import Participant
from backend.room.models import Room


def send_invite(
    inviter: User,
    room: Room,
    invitee: User,
    role: Optional[Role],
    expires_at: Optional[datetime],
) -> Invite:
    data = {"expires_at": expires_at}
    form = InviteForm(data=data)

    if not form.is_valid():
        raise FormValidationException("Invalid invite data", errors=form.errors)

    try:
        invite = form.save(commit=False)
        invite.inviter = inviter
        invite.invitee = invitee
        invite.role = role
        invite.room = room
        invite.save()
    except IntegrityError as e:
        raise ConflictException("Could not send invite due to a conflict.") from e

    return invite


def accept_invite(user: User, invite: Invite) -> Participant:
    try:
        with transaction.atomic():
            participant = Participant.objects.create(
                user=user,
                room=invite.room,
                role=invite.role,
            )

            invite.update_status(Invite.Status.ACCEPTED)
    except IntegrityError as e:
        raise ConflictException("User is already a participant of this room.") from e

    return participant


def decline_invite(invite: Invite) -> Invite:
    invite.update_status(Invite.Status.DECLINED)
    return invite


def cancel_invite(invite: Invite) -> Invite:
    invite.update_status(Invite.Status.REVOKED)
    return invite


def resend_invite(invite: Invite, new_expires_at: Optional[datetime]) -> Invite:
    data = {"expires_at": new_expires_at}
    form = InviteForm(data=data, instance=invite)

    if not form.is_valid():
        raise FormValidationException("Invalid invite data", errors=form.errors)

    form.save()
    return invite
