import uuid
from datetime import datetime
from typing import Optional

from django.db import IntegrityError, transaction
from django.utils import timezone

from backend.core.models import User
from backend.invite.models import Invite
from backend.room.models import Room
from backend.access.models import Role, Participant
from backend.core.forms import InviteForm
from backend.core.exceptions import (
    FormValidationException,
    PermissionException,
    ConflictException,
    ValidationException,
)
from backend.access.services import RoleService
from backend.access.enums import PermissionCode


class InviteService:
    """Service for invite mutation operations."""
    
    @staticmethod
    def _update_expired_invites() -> None:
        """
        Lazy update: Mark all expired pending invites as EXPIRED.
        Should be called whenever an invite is fetched.
        """
        Invite.objects.filter(
            status=Invite.InviteStatus.PENDING,
            expires_at__lt=timezone.now()
        ).update(status=Invite.InviteStatus.EXPIRED)
    
    @staticmethod
    def send_invite(
        inviter: User,
        room: Room,
        invitee: User,
        role: Role,
        expires_at: datetime,
    ) -> Invite:
        """
        Send an invite to a user for a room.
        
        Args:
            inviter: User sending the invite (must have ROOM_SEND_INVITE permission)
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
        if not Participant.objects.filter(user=inviter, room=room).exists():
            raise PermissionException("You must be a participant of the room to send invites.")
        
        if not RoleService.has_permission(inviter, room, PermissionCode.ROOM_SEND_INVITE):
            raise PermissionException("You don't have permission to invite users to this room.")
        
        if Participant.objects.filter(user=invitee, room=room).exists():
            raise ValidationException("The user is already a participant of this room.")
        
        if role.room != room:
            raise ValidationException("Role must belong to the same room.")
        
        if Invite.active_invites(invitee=invitee, room=room).exists():
            raise ConflictException("This user already has an active invite to this room.")
        
        data = {
            "expires_at": expires_at,
        }
        
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
        if invite.invitee != user:
            raise PermissionException("You can only accept invites sent to you.")
        
        if invite.status != Invite.InviteStatus.PENDING:
            raise ValidationException(f"Invite is '{invite.status.lower()}' and cannot be accepted.")
        
        try:
            with transaction.atomic():
                participant = Participant.objects.create(
                    user=user,
                    room=invite.room,
                    role=invite.role
                )
                
                invite.status = Invite.InviteStatus.ACCEPTED
                invite.save(update_fields=["status"])
                
        except IntegrityError as e:
            raise ConflictException("User is already a participant of this room.") from e
    
        return participant
    
    @staticmethod
    def decline_invite(user: User, invite: Invite) -> bool:
        """
        Decline an invite.
        
        Args:
            user: User declining the invite (must be the invitee)
            invite: The invite to decline
            
        Returns:
            True if decline was successful
            
        Raises:
            PermissionException: If user is not the invitee
            ValidationException: If invite is not pending
        """
        if invite.invitee != user:
            raise PermissionException("You can only decline invites sent to you.")
        
        if invite.status != Invite.InviteStatus.PENDING:
            raise ValidationException(f"Invite is {invite.status.lower()} and cannot be declined.")
        
        invite.status = Invite.InviteStatus.DECLINED
        invite.save(update_fields=["status"])
        
        return True
    
    # TODO: rework
    @staticmethod
    def cancel_invite(user: User, invite: Invite) -> bool:
        """
        Cancel a pending invite (inviter only).
        
        Args:
            user: User canceling the invite (must be the inviter)
            invite: The invite to cancel
            
        Returns:
            True if cancel was successful
            
        Raises:
            PermissionException: If user is not the inviter
            ValidationException: If invite is not pending
        """
        if invite.inviter != user:
            raise PermissionException("Only the inviter can cancel an invite.")
        
        if invite.status != Invite.InviteStatus.PENDING:
            raise ValidationException(f"Invite is {invite.status.lower()} and cannot be canceled.")
        
        invite.delete()
        
        return True
    
    @staticmethod
    def _update_if_expired(invite: Invite) -> None:
        """
        Check if invite has expired and update status if needed.
        
        Args:
            invite: The invite to check
        """
        if invite.is_expired and invite.status != Invite.InviteStatus.EXPIRED:
            invite.status = Invite.InviteStatus.EXPIRED
            invite.save(update_fields=["status"])
    
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
            invite = Invite.objects.select_related('inviter', 'invitee', 'role').get(token=token)
        except Invite.DoesNotExist:
            return None
        
        InviteService._update_if_expired(invite)
        invite.refresh_from_db(fields=["status"])
        
        return invite
