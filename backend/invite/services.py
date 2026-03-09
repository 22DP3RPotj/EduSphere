import uuid
from datetime import datetime
from typing import Optional

from backend.account.models import User
from backend.invite.models import Invite
from backend.room.models import Room
from backend.access.models import Role, Participant
from backend.core.exceptions import (
    PermissionException,
    ConflictException,
    ValidationException,
)
from backend.invite.rules.labels import InvitePermission
from backend.invite import actions


class InviteService:
    """Service for invite mutation operations."""

    @staticmethod
    def send_invite(
        inviter: User,
        room: Room,
        invitee: User,
        role: Optional[Role] = None,
        expires_at: Optional[datetime] = None,
    ) -> Invite:
        """
        Send an invite to a user for a room.

        Args:
            inviter: User sending the invite (must have ROOM_MANAGE_PARTICIPANTS permission)
            room: The room to invite to
            invitee: The user being invited
            role: The role to assign the invitee
            expires_at: When the invite expires

        Returns:
            The created Invite instance

        Raises:
            PermissionException: If inviter doesn't have permission
            ValidationException: If invitee is already a participant or role doesn't belong to room
            ConflictException: If invite creation conflicts
            FormValidationException: If form validation fails
        """
        if not inviter.has_perm(InvitePermission.CREATE, room):
            raise PermissionException(
                "You don't have permission to invite users to this room."
            )

        if Participant.objects.filter(user=invitee, room=room).exists():
            raise ValidationException("The user is already a participant of this room.")

        if role and role.room != room:
            raise ValidationException("Role must belong to the same room.")

        if Invite.objects.filter(invitee=invitee, room=room).active().exists():
            raise ConflictException(
                "This user already has an active invite to this room."
            )

        return actions.send_invite(
            inviter=inviter,
            room=room,
            invitee=invitee,
            role=role,
            expires_at=expires_at,
        )

    @staticmethod
    def accept_invite(user: User, invite: Invite) -> Participant:
        """
        Accept an invite.

        Args:
            user: User accepting the invite (must be the invitee)
            invite: The invite to accept

        Returns:
            The created Participant instance

        Raises:
            PermissionException: If user is not the invitee
            ValidationException: If invite is not pending
            ConflictException: If user is already a participant
        """
        if not user.has_perm(InvitePermission.ACCEPT, invite):
            raise PermissionException(
                "You don't have permission to accept this invite."
            )

        if invite.status != Invite.Status.PENDING:
            raise ValidationException(
                f"Invite is '{invite.status.lower()}' and cannot be accepted."
            )

        return actions.accept_invite(user=user, invite=invite)

    @staticmethod
    def decline_invite(user: User, invite: Invite) -> Invite:
        """
        Decline an invite.

        Args:
            user: User declining the invite (must be the invitee)
            invite: The invite to decline

        Returns:
            The updated Invite instance

        Raises:
            PermissionException: If user is not the invitee
            ValidationException: If invite is not pending
        """
        if invite.invitee != user:
            raise PermissionException("You are not the invitee for this invite.")

        if not user.has_perm(InvitePermission.REJECT, invite):
            raise PermissionException(
                "You don't have permission to reject this invite."
            )

        if not invite.is_active:
            raise ValidationException(
                f"Invite is {invite.status.lower()} and cannot be declined."
            )

        return actions.decline_invite(invite=invite)

    @staticmethod
    def cancel_invite(user: User, invite: Invite) -> Invite:
        """
        Cancel a pending invite (inviter only).

        Args:
            user: User canceling the invite (must be the inviter)
            invite: The invite to cancel

        Returns:
            The updated Invite instance

        Raises:
            PermissionException: If user is not the inviter
            ValidationException: If invite is not pending
        """
        if not user.has_perm(InvitePermission.DELETE, invite):
            raise PermissionException(
                "You don't have permission to cancel this invite."
            )

        if not invite.is_active:
            raise ValidationException(
                f"Invite is {invite.status.lower()} and cannot be canceled."
            )

        return actions.cancel_invite(invite=invite)

    @staticmethod
    def resend_invite(user: User, invite: Invite, new_expires_at: datetime) -> Invite:
        """
        Resend an invite by updating its expiration date.

        Args:
            user: User resending the invite (must have ROOM_MANAGE_PARTICIPANTS permission)
            invite: The invite to resend
            new_expires_at: New expiration datetime

        Returns:
            The updated Invite instance

        Raises:
            PermissionException: If user does not have ROOM_MANAGE_PARTICIPANTS permission
            ValidationException: If invite is already resolved (accepted or declined)
        """

        if not user.has_perm(InvitePermission.UPDATE, invite):
            raise PermissionException(
                "You don't have permission to resend this invite."
            )

        if invite.is_resolved:
            raise ValidationException("Cannot resend a resolved invite.")

        return actions.resend_invite(invite=invite, new_expires_at=new_expires_at)

    @staticmethod
    def get_invite_by_token(token: uuid.UUID) -> Optional[Invite]:
        """
        Get an invite by its token.

        Automatically checks and updates expiration status.

        Args:
            token: The invite token

        Returns:
            The Invite instance if valid token, None otherwise
        """
        try:
            invite = Invite.objects.select_related("inviter", "invitee", "role").get(
                token=token
            )
        except Invite.DoesNotExist:
            return None

        return actions.update_if_expired(invite=invite)
