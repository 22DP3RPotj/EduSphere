from django.db import IntegrityError

from backend.messaging.models import Message
from backend.account.models import User
from backend.room.models import Room
from backend.access.models import Participant

from backend.core.forms import MessageForm
from backend.core.exceptions import (
    FormValidationException,
    PermissionException,
    ConflictException
)
from backend.access.services import RoleService
from backend.access.enums import PermissionCode


class MessageService:
    """Service for message mutation operations."""
    
    @staticmethod
    def create_message(
        user: User,
        room: Room,
        body: str,
    ) -> Message:
        """
        Create a new message in a room.
        
        Args:
            user: User creating the message (must be a participant of the room)
            room: The room to create the message in
            body: Message content
            
        Returns:
            The created Message instance
            
        Raises:
            PermissionException: If user is not a participant of the room
            FormValidationException: If form validation fails
            ConflictException: If message creation conflicts
        """
        participant = Participant.objects.filter(user=user, room=room).first()
        
        if participant is None:
            raise PermissionException("You must be a participant of the room to send messages.")
        
        data = {
            "body": body,
        }
        
        form = MessageForm(data=data)
        
        if not form.is_valid():
            raise FormValidationException("Invalid message data", errors=form.errors)
        
        try:
            message = form.save(commit=False)
            message.user = user
            message.room = room
            message.save()
        except IntegrityError as e:
            raise ConflictException("Could not create message due to a conflict.") from e
    
        return message
    
    @staticmethod
    def update_message(
        user: User,
        message: Message,
        body: str,
    ) -> Message:
        """
        Update a message.
        
        Args:
            user: User performing the update (must be the message author)
            message: The message to update
            body: New message content
            
        Returns:
            The updated Message instance
            
        Raises:
            PermissionException: If user is not the message author
            FormValidationException: If form validation fails
            ConflictException: If update conflicts
        """
        if message.user != user:
            raise PermissionException("You can only edit your own messages.")
        
        data = {
            "body": body,
        }
        
        form = MessageForm(data=data, instance=message)
        
        if not form.is_valid():
            raise FormValidationException("Invalid message data", errors=form.errors)
        
        try:
            message = form.save(commit=False)
            if not message.is_edited:
                message.is_edited = True
            message.save()
        except IntegrityError as e:
            raise ConflictException("Could not update message due to a conflict.") from e

        return message
    
    @staticmethod
    def delete_message(
        user: User,
        message: Message,
    ) -> bool:
        """
        Delete a message.
        
        Args:
            user: User performing the deletion (must be the author or have delete permission)
            message: The message to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            PermissionException: If user doesn't have permission to delete the message
        """
        # User can delete their own messages or must have ROOM_DELETE_MESSAGE permission
        if message.user != user:
            if not RoleService.has_permission(user, message.room, PermissionCode.ROOM_DELETE_MESSAGE):
                raise PermissionException("You don't have permission to delete this message.")
        
        message.delete()
        return True
    
    @staticmethod
    def serialize(message: Message) -> dict:
        """
        Serialize a message to a dictionary.
        
        Args:
            message: The message to serialize
            
        Returns:
            Dictionary representation of the message
        """
        return {
            'id': str(message.id),
            'user': message.user.username,
            'user_id': str(message.user.id),
            'body': message.body,
            'is_edited': message.is_edited,
            'created_at': message.created_at.isoformat(),
            'updated_at': message.updated_at.isoformat(),
            'user_avatar': message.user.avatar.name if message.user.avatar else None,
        }
