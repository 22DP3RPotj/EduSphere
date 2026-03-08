import uuid
from typing import Optional

from django.db.models import QuerySet

from backend.account.models import User
from backend.room.models import Room

from backend.core.exceptions import (
    PermissionException,
    ValidationException,
)
from backend.access.models import Participant, Role
from backend.access.rules.labels import AccessPermission
from backend.access.enums import PermissionCode
from backend.access.dtos import RoleDeleteResult
from backend.access import actions


class RoleService:
    """Service for role-related operations."""

    # @staticmethod
    # def _ensure_can_manage_roles(user: User, room: Room) -> Participant:
    #     """Centralized authorization check."""
    #     participant = RoleService.get_participant(user, room)

    #     if not participant:
    #         raise PermissionException("User is not a member of this room.")

    #     if not participant.role or not RoleService.has_permission(
    #         user, room, PermissionCode.ROOM_MANAGE_ROLES
    #     ):
    #         raise PermissionException("Missing ROOM_MANAGE_ROLES permission.")

    #     return participant

    # @staticmethod
    # def _validate_hierarchy(actor: Participant, target_priority: int):
    #     """Ensures the actor has a higher priority than the role they are creating/modifying."""
    #     if actor.role is None:
    #         raise PermissionException(
    #             "You do not have a role and cannot manage others."
    #         )

    #     if target_priority >= actor.role.priority:
    #         raise PermissionException(
    #             f"Priority {target_priority} exceeds your capacity."
    #         )

    # @staticmethod
    # def _validate_permissions_subset(
    #     actor: Participant, requested_ids: list[uuid.UUID]
    # ):
    #     """Ensures user isn't granting permissions they don't have (Escalation prevention)."""
    #     if actor.role is None:
    #         raise PermissionException(
    #             "You do not have a role and cannot manage others."
    #         )

    #     user_perms = {p.id for p in actor.role.permissions.all()}
    #     if not set(requested_ids).issubset(user_perms):
    #         raise PermissionException("Cannot grant permissions you do not possess.")

    @staticmethod
    def _is_valid_permission_set(
        participant: Participant,
        permission_ids: list[uuid.UUID],
    ) -> bool:
        """
        Check if a permission set is valid for a certain participant
        User can't modify permissions they don't have

        Args:
            participant: The user attempting the action
            permission_ids: The permission set as list of ids

        Returns:
            True if permission set is valid, False otherwise
        """
        if participant.role is None:
            return False

        user_perms = {p.id for p in participant.role.permissions.all()}
        requested_perms = set(permission_ids)

        return requested_perms.issubset(user_perms)

    @staticmethod
    def can_affect_role(participant: Participant, target_role: Role) -> bool:
        """
        Check if a user can affect a target role based on priority hierarchy.
        Higher priority values = higher privilege users (can affect lower priority values).

        Args:
            participant: The user attempting the action
            target_role: The target role

        Returns:
            True if user can affect the target role, False otherwise
        """

        if participant.role is None:
            return False

        return participant.role.priority > target_role.priority

    @staticmethod
    def has_permission(user: User, room: Room, perm_code: PermissionCode) -> bool:
        """
        Check if a user has a specific permission in a room.

        Args:
            user: The user
            room: The room
            perm_code: The permission code to check

        Returns:
            True if the user has the permission, False otherwise
        """
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return Participant.objects.filter(
            user=user, room=room, role__permissions__code=perm_code
        ).exists()

    @staticmethod
    def get_room_roles(room: Room) -> QuerySet[Role]:
        """
        Get all roles in a room.

        Args:
            room: The room to get roles from

        Returns:
            QuerySet of roles
        """
        return Role.objects.filter(room=room).prefetch_related("permissions")

    @staticmethod
    def get_role_by_id(role_id: uuid.UUID) -> Optional[Role]:
        """
        Get a role with optimized prefetch_related queries.

        Args:
            role_id: The ID of the role to fetch

        Returns:
            The Role instance or None if not found
        """
        try:
            role = (
                Role.objects.select_related("room")
                .prefetch_related("permissions")
                .get(id=role_id)
            )
        except Role.DoesNotExist:
            return None

        return role

    @staticmethod
    def get_participant(user: User, room: Room) -> Optional[Participant]:
        """
        Get a participant by user and room

        Args:
            user: The user
            room: The room

        Returns:
            The Participant instance or None if not found
        """
        try:
            participant = (
                Participant.objects.select_related("role")
                .prefetch_related("role__permissions")
                .get(user=user, room=room)
            )
        except Participant.DoesNotExist:
            return None

        return participant

    @staticmethod
    def create_default_roles(room: Room) -> None:
        """
        Create default roles for a room. Should be called once when the room is created.

        Args:
            room: The room
        """
        actions.create_default_roles(room=room)

    @staticmethod
    def create_role(
        user: User,
        room: Room,
        name: str,
        description: Optional[str],
        priority: int,
        permission_ids: list[uuid.UUID],
    ) -> Role:
        """
        Create a new role in a room.

        Args:
            user: User creating the role (must have ROOM_MANAGE_ROLES permission)
            room: The room to create the role in
            name: Role name
            description: Role description
            priority: Role priority (0-100, higher = higher priority)
            permission_ids: List of permission IDs to assign

        Returns:
            The created Role instance

        Raises:
            PermissionException: If user doesn't have ROOM_MANAGE_ROLES permission
            ValidationException: If form validation fails
            ConflictException: If role creation conflicts
        """
        participant = RoleService.get_participant(user, room)

        if participant is None:
            raise PermissionException(
                "You are not a participant of this room and cannot create roles."
            )

        if participant.role is None or not RoleService.has_permission(
            user, room, PermissionCode.ROOM_MANAGE_ROLES
        ):
            raise PermissionException(
                "You don't have permission to manage roles in this room."
            )

        user_priority = participant.role.priority

        if priority >= user_priority:
            raise PermissionException(
                f"Cannot create roles with priority equal to or higher than your own. "
                f"Your priority: {user_priority}, "
                f"Attempted priority: {priority}"
            )

        if permission_ids:
            if not RoleService._is_valid_permission_set(participant, permission_ids):
                raise PermissionException(
                    "Cannot assign permissions you don't have. "
                    "You can only grant permissions your role already possesses."
                )

        return actions.create_role(
            room=room,
            name=name,
            description=description,
            priority=priority,
            permission_ids=permission_ids,
        )

    @staticmethod
    def update_role(
        user: User,
        role: Role,
        name: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        permission_ids: Optional[list[uuid.UUID]] = None,
    ) -> Role:
        """
        Update a role.

        Args:
            user: User performing the update (must have ROOM_MANAGE_ROLES permission)
            role: The role to update
            name: New role name (optional)
            description: New role description (optional)
            priority: New role priority (optional)
            permission_ids: New list of permission IDs (optional)

        Returns:
            The updated Role instance

        Raises:
            PermissionException: If user doesn't have permission or priority hierarchy violation
            ValidationException: If form validation fails
            ConflictException: If update conflicts
        """
        if not user.has_perm(AccessPermission.UPDATE, role):
            raise PermissionException("You don't have permission to update this role.")

        if permission_ids is not None:
            participant = RoleService.get_participant(user, role.room)
            if participant is not None and not RoleService._is_valid_permission_set(
                participant, permission_ids
            ):
                raise PermissionException(
                    "Cannot assign permissions you don't have. "
                    "You can only grant permissions your role already possesses."
                )

        return actions.update_role(
            role=role,
            name=name,
            description=description,
            priority=priority,
            permission_ids=permission_ids,
        )

    @staticmethod
    def delete_role(
        user: User, role: Role, substitution_role: Optional[Role] = None
    ) -> RoleDeleteResult:
        """
        Delete a role.

        Args:
            user: User performing the deletion (must have ROOM_MANAGE_ROLES permission)
            role: The role to delete
            substitution_role: Role to reassign participants and invites to (required if role has participants/invites)

        Returns:
            Dictionary with deletion status and reassignment counts:
            {
                'success': bool,
                'participants_reassigned': int,
                'invites_reassigned': int
            }

        Raises:
            PermissionException: If user doesn't have permission or priority hierarchy violation
            ValidationException: If role has participants/invites but no substitution role provided
        """
        if not user.has_perm(AccessPermission.DELETE, role):
            raise PermissionException("You don't have permission to delete this role.")

        return actions.delete_role(role=role, substitution_role=substitution_role)

    @staticmethod
    def assign_permissions_to_role(
        user: User,
        role: Role,
        permission_ids: list[uuid.UUID],
    ) -> Role:
        """
        Assign permissions to a role.

        Args:
            user: User performing the assignment (must have ROOM_MANAGE_ROLES permission)
            role: The role to assign permissions to
            permission_ids: List of permission IDs

        Returns:
            The updated Role instance

        Raises:
            PermissionException: If user doesn't have permission, priority violation, or permission escalation attempt
        """
        if not user.has_perm(AccessPermission.UPDATE, role):
            raise PermissionException(
                "You don't have permission to assign permissions to this role."
            )

        participant = RoleService.get_participant(user, role.room)
        if participant is not None and not RoleService._is_valid_permission_set(
            participant, permission_ids
        ):
            raise PermissionException(
                "Cannot assign permissions you don't have. "
                "You can only grant permissions your role already possesses."
            )

        return actions.assign_permissions_to_role(
            role=role,
            permission_ids=permission_ids,
        )

    @staticmethod
    def remove_permissions_from_role(
        user: User,
        role: Role,
        permission_ids: list[uuid.UUID],
    ) -> Role:
        """
        Remove permissions from a role.

        Args:
            user: User performing the removal (must have ROOM_MANAGE_ROLES permission)
            role: The role to remove permissions from
            permission_ids: List of permission IDs to remove

        Returns:
            The updated Role instance

        Raises:
            PermissionException: If user doesn't have permission or priority hierarchy violation
        """
        if not user.has_perm(AccessPermission.UPDATE, role):
            raise PermissionException(
                "You don't have permission to remove permissions from this role."
            )

        return actions.remove_permissions_from_role(
            role=role,
            permission_ids=permission_ids,
        )


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
                Participant.objects.select_related("user", "role")
                .prefetch_related("role__permissions")
                .get(user=user, room=room)
            )
        except Participant.DoesNotExist:
            return None

        return participant

    @staticmethod
    def add_participant(
        room: Room,
        user: User,
        role: Optional[Role],
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
        return actions.add_participant(room=room, user=user, role=role)

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

        if not user.has_perm(AccessPermission.UPDATE, new_role):
            raise PermissionException("You don't have permission to assign this role.")

        return actions.change_participant_role(
            participant=participant, new_role=new_role
        )

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
            if participant.role is None:
                raise ValidationException("Participant has no role assigned.")

            if not user.has_perm(AccessPermission.UPDATE, participant.role):
                raise PermissionException(
                    "You don't have permission to remove this participant."
                )

        return actions.remove_participant(participant=participant)

    @staticmethod
    def get_user_rooms(user: User):
        """
        Get all rooms where a user is a participant (helper method).

        Args:
            user: The user

        Returns:
            QuerySet of rooms
        """
        return (
            Room.objects.filter(participants=user)
            .prefetch_related("topics", "participants")
            .select_related("host")
        )
