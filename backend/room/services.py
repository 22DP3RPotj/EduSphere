from typing import Optional

from backend.account.models import User
from backend.room.choices import VisibilityChoices
from backend.room.models import Room
from backend.core.exceptions import (
    PermissionException,
)
from backend.room import actions
from backend.room.rules.labels import RoomPermission


class RoomService:
    """Service for room mutation operations."""

    @staticmethod
    def create_room(
        *,
        user: User,
        name: str,
        description: str,
        topic_names: list[str],
        visibility: Optional[VisibilityChoices] = None,
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
        return actions.create_room(
            user=user,
            name=name,
            description=description,
            topic_names=topic_names,
            visibility=visibility,
        )

    @staticmethod
    def update_room(
        *,
        user: User,
        room: Room,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[VisibilityChoices] = None,
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
        if not user.has_perm(RoomPermission.UPDATE, room):
            raise PermissionException(
                "You don't have the permission to update this room."
            )

        return actions.update_room(
            room=room,
            name=name,
            description=description,
            visibility=visibility,
            topic_names=topic_names,
        )

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
        if not user.has_perm(RoomPermission.DELETE, room):
            raise PermissionException(
                "You don't have the permission to delete this room."
            )

        return actions.delete_room(room=room)
