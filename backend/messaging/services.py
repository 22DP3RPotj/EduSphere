from backend.messaging.models import Message
from backend.account.models import User
from backend.room.models import Room
from backend.core.exceptions import (
    PermissionException,
)
from backend.messaging.rules.labels import MessagingPermission
from backend.messaging import actions


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
            PermissionException: If user doesn't have permission to send messages
            FormValidationException: If form validation fails
            ConflictException: If message creation conflicts
        """
        if not user.has_perm(MessagingPermission.CREATE, room):
            raise PermissionException(
                "You don't have permission to send messages in this room."
            )

        return actions.create_message(user=user, room=room, body=body)

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
        if not user.has_perm(MessagingPermission.UPDATE, message):
            raise PermissionException("You can only edit your own messages.")

        return actions.update_message(message=message, body=body)

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
        if not user.has_perm(MessagingPermission.DELETE, message):
            raise PermissionException(
                "You don't have permission to delete this message."
            )

        return actions.delete_message(message=message)

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
            "id": str(message.id),
            "author": message.author.username,
            "author_id": str(message.author.id),
            "body": message.body,
            "is_edited": message.is_edited,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "author_avatar": (
                message.author.avatar.name if message.author.avatar else None
            ),
        }
