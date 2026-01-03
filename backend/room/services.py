from typing import Optional

from django.db import IntegrityError, transaction

from backend.account.models import User
from backend.room.choices import RoomVisibility
from backend.room.models import Room, Topic
from backend.access.models import Participant
from backend.core.forms import RoomForm
from backend.core.exceptions import (
    FormValidationException,
    PermissionException,
    ConflictException
)
from backend.access.services import RoleService
from backend.access.enums import RoleCode, PermissionCode

class RoomService:
    """Service for room mutation operations."""
    @staticmethod
    def can_view(user: User, room: Room) -> bool:
        is_participant = Participant.objects.filter(
            user=user, room=room
        ).exists()
        
        is_public = room.visibility == RoomVisibility.PUBLIC
        
        return is_participant or is_public
    
    @staticmethod
    def create_room(
        *,
        user: User,
        name: str,
        description: str,
        topic_names: list[str],
        visibility: Optional[RoomVisibility] = None,
    ) -> Room:
        """
        Create a new room.
        
        Args:
            user: User creating the room (becomes the host/owner)
            name: Room name
            description: Room description
            visibility: Room visibility (PUBLIC or PRIVATE)
            topic_names: List of topic names to associate with the room
            
        Returns:
            The created Room instance
            
        Raises:
            FormValidationException: If form validation fails
            ConflictException: If room creation conflicts
        """
        data = {
            "name": name,
            "description": description,
        }
        
        form = RoomForm(data=data)
        
        if not form.is_valid():
            raise FormValidationException("Invalid room data", errors=form.errors)
        
        with transaction.atomic():
            room: Room = form.save(commit=False)
            room.host = user
            if visibility is not None:
                room.visibility = visibility
            room.save()
            
            topics = [
                Topic.objects.get_or_create(name=topic_name)[0]
                for topic_name in topic_names
            ]
            room.topics.set(topics)
            
            RoleService.create_default_roles(room)
            
            member_role = room.roles.get(name=RoleCode.MEMBER.label)
            room.default_role = member_role
            room.save(update_fields=["default_role"])
            
            owner_role = room.roles.get(name=RoleCode.OWNER.label)
            
            try:
                Participant.objects.create(
                    user=user,
                    room=room,
                    role=owner_role
                )
            except IntegrityError as e:
                raise ConflictException("Could not create room due to a conflict.") from e
    
        return room
    
    @staticmethod
    def update_room(
        *,
        user: User,
        room: Room,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[RoomVisibility] = None,
        topic_names: Optional[list[str]] = None,
    ) -> Room:
        """
        Update a room.
        
        Args:
            user: User performing the update (must have ROOM_UPDATE permission)
            room: The room to update
            name: New room name (optional)
            description: New room description (optional)
            visibility: New visibility (optional)
            topic_names: New list of topic names (optional)
            
        Returns:
            The updated Room instance
            
        Raises:
            PermissionException: If user doesn't have permission
            FormValidationException: If form validation fails
            ConflictException: If update conflicts
        """
        if not RoleService.has_permission(user, room, PermissionCode.ROOM_UPDATE):
            raise PermissionException("You don't have the permission to update this room.")
        
        data = {
            "name": name if name is not None else room.name,
            "description": description if description is not None else room.description,
        }
        
        try:
            with transaction.atomic():
                form = RoomForm(data=data, instance=room)
                
                if not form.is_valid():
                    raise FormValidationException("Invalid room data", errors=form.errors)
                
                form.save()
                
                if topic_names is not None:
                    topics = [
                        Topic.objects.get_or_create(name=topic_name)[0]
                        for topic_name in topic_names
                    ]
                    room.topics.set(topics)
                
                if visibility is not None:
                    room.visibility = visibility
                    room.save(update_fields=["visibility"])
        except IntegrityError as e:
            raise ConflictException("Could not update room due to a conflict.") from e
    
        return room
    
    @staticmethod
    def delete_room(user: User, room: Room) -> bool:
        """
        Delete a room.
        
        Args:
            user: User performing the deletion (must have ROOM_DELETE permission)
            room: The room to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            PermissionException: If user doesn't have permission
            ConflictException: If deletion conflicts
        """
        if not RoleService.has_permission(user, room, PermissionCode.ROOM_DELETE):
            raise PermissionException("You don't have the permission to delete this room.")
        
        room.delete()
        return True
