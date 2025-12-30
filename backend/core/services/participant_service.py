from typing import Optional

from django.db import IntegrityError

from backend.core.models import User, Room
from backend.access.models import Role, Participant
from backend.access.enums import PermissionCode
from backend.core.exceptions import PermissionException, ConflictException, ValidationException
from backend.core.services.role_service import RoleService


class ParticipantService:
    """Service for participant mutation operations."""
    
    @staticmethod
    def get_participant(user: User, room: Room) -> Optional[Participant]:
        """
        Get a participant by user and room (helper method).
        
        Args:
            user: The user
            room: The room
            
        Returns:
            The Participant instance or None if not found
        """
        try:
            participant = (
                Participant.objects
                .select_related('user', 'role')
                .prefetch_related('role__permissions')
                .get(user=user, room=room)
            )
        except Participant.DoesNotExist:
            return None
        
        return participant
    
    @staticmethod
    def add_participant(
        room: Room,
        user: User,
        role: Role,
    ) -> Participant:
        """
        Add a participant to a room.
        
        Args:
            room: The room
            user: The user to add
            role: The role to assign to the user
            
        Returns:
            The created Participant instance
            
        Raises:
            ValidationException: If role doesn't belong to the room
            ConflictException: If user is already a participant
        """
        if role.room != room:
            raise ValidationException("Role must belong to the same room.")
        
        if Participant.objects.filter(user=user, room=room).exists():
            raise ConflictException("User is already a participant of this room.")
        
        try:
            participant = Participant.objects.create(
                user=user,
                room=room,
                role=role
            )
        except IntegrityError as e:
            raise ConflictException("User is already a participant of this room.") from e
    
        return participant
    
    @staticmethod
    def change_participant_role(
        user: User,
        participant: Participant,
        new_role: Role,
    ) -> Participant:
        """
        Change a participant's role.
        
        Args:
            user: User performing the action (must have role management permission)
            participant: The participant to update
            new_role: The new role
            
        Returns:
            The updated Participant instance
            
        Raises:
            PermissionException: If user doesn't have permission
            ValidationException: If role doesn't belong to the room
        """
        if new_role.room != participant.room:
            raise ValidationException("New role must belong to the same room.")
        
        if not RoleService.has_permission(user, participant.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage participant roles.")
        
        user_participant = RoleService.get_participant(user, participant.room)
        if user_participant is None:
            raise PermissionException("You must be a participant to manage roles.")
        
        if not RoleService.can_affect_role(user_participant, new_role):
            raise PermissionException("Cannot assign roles with higher or equal priority.")
        
        participant.role = new_role
        participant.save()
        
        return participant
    
    @staticmethod
    def remove_participant(
        user: User,
        participant: Participant,
    ) -> bool:
        """
        Remove a participant from a room.
        
        Args:
            user: User performing the removal (must be the participant or have permission)
            participant: The participant to remove
            
        Returns:
            True if removal was successful
            
        Raises:
            PermissionException: If user doesn't have permission
        """
        # User can remove themselves or must have role management permission
        if user != participant.user:
            if not RoleService.has_permission(user, participant.room, PermissionCode.ROOM_ROLE_MANAGE):
                raise PermissionException("You don't have permission to remove participants.")
            
            user_participant = RoleService.get_participant(user, participant.room)
            if user_participant is None:
                raise PermissionException("You must be a participant to remove others.")
            
            if not RoleService.can_affect_role(user_participant, participant.role):
                raise PermissionException("Cannot remove participants with higher or equal role priority.")
        
        participant.delete()
        return True
    
    @staticmethod
    def get_user_rooms(user: User):
        """
        Get all rooms where a user is a participant (helper method).
        
        Args:
            user: The user
            
        Returns:
            QuerySet of rooms
        """
        return Room.objects.filter(
            participants=user
        ).prefetch_related('topics', 'participants').select_related('host')
