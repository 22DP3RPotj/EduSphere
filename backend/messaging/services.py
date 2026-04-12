import uuid

from backend.messaging.models import Message, MessageStatus
from backend.messaging.choices import MessageStatusChoices
from backend.account.models import User
from backend.room.models import Room
from backend.core.exceptions import (
    PermissionException,
    NotFoundException,
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
        parent_id: uuid.UUID | None = None,
    ) -> Message:
        """
        Create a new message in a room.

        Args:
            user: User creating the message (must be a participant of the room)
            room: The room to create the message in
            body: Message content
            parent_id: Optional UUID of the parent message (for replies)

        Returns:
            The created Message instance

        Raises:
            PermissionException: If user doesn't have permission to send messages
            NotFoundException: If parent message doesn't exist or is in a different room
            FormValidationException: If form validation fails
            ConflictException: If message creation conflicts
        """
        if not user.has_perm(MessagingPermission.CREATE, room):
            raise PermissionException(
                "You don't have permission to send messages in this room."
            )

        parent = None
        if parent_id is not None:
            try:
                parent = Message.objects.select_related("author").get(id=parent_id)
            except Message.DoesNotExist:
                raise NotFoundException("Parent message not found.")
            if parent.room_id != room.id:
                raise NotFoundException("Parent message not found.")

        return actions.create_message(user=user, room=room, body=body, parent=parent)

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
        parent_preview = None
        if message.parent_id is not None:
            parent = message.parent
            if parent is not None:
                parent_preview = {
                    "id": str(parent.id),
                    "body": parent.body[:100],
                    "author": parent.author.username,
                }

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
            "parent_id": str(message.parent_id) if message.parent_id else None,
            "parent_preview": parent_preview,
        }


class MessageStatusService:
    """Service for message delivery/read status operations."""

    @staticmethod
    def mark_delivered(user: User, message_ids: list[uuid.UUID]) -> list[MessageStatus]:
        """
        Bulk-create DELIVERED statuses for messages not authored by the user.
        Uses ignore_conflicts to skip already-delivered messages.
        """
        messages = Message.objects.filter(id__in=message_ids).exclude(author=user)

        statuses = [
            MessageStatus(
                message=msg,
                user=user,
                status=MessageStatusChoices.DELIVERED,
            )
            for msg in messages
        ]
        return MessageStatus.objects.bulk_create(statuses, ignore_conflicts=True)

    @staticmethod
    def mark_seen(user: User, message_ids: list[uuid.UUID]) -> list[dict]:
        """
        Mark messages as SEEN for the user. Upgrades DELIVERED → SEEN.
        Returns list of updates that were actually applied (for broadcasting).
        """
        messages = Message.objects.filter(id__in=message_ids).exclude(author=user)

        updates = []
        for msg in messages:
            _, created = MessageStatus.objects.update_or_create(
                message=msg,
                user=user,
                defaults={"status": MessageStatusChoices.SEEN},
            )
            updates.append(
                {
                    "message_id": str(msg.id),
                    "user_id": str(user.id),
                    "status": MessageStatusChoices.SEEN,
                }
            )

        return updates

    @staticmethod
    def get_status_summary(message_ids: list[uuid.UUID]) -> dict[str, dict]:
        """
        Get aggregated status counts per message.
        Returns {message_id_str: {"delivered": int, "seen": int}}
        """
        from django.db.models import Count, Q

        statuses = (
            MessageStatus.objects.filter(message_id__in=message_ids)
            .values("message_id")
            .annotate(
                delivered=Count(
                    "id",
                    filter=Q(status=MessageStatusChoices.DELIVERED),
                ),
                seen=Count(
                    "id",
                    filter=Q(status=MessageStatusChoices.SEEN),
                ),
            )
        )

        summary = {}
        for row in statuses:
            summary[str(row["message_id"])] = {
                "delivered": row["delivered"],
                "seen": row["seen"],
            }
        return summary
