import uuid
from typing import Optional

from django.db import IntegrityError, transaction
from django.db.models import QuerySet

from backend.account.models import User
from backend.invite.models import Invite
from backend.room.models import Room
from backend.access.models import Participant, Role, Permission
from backend.access.enums import PermissionCode
from backend.core.forms import RoleForm
from backend.core.exceptions import (
    FormValidationException,
    PermissionException,
    ConflictException,
    ValidationException
)
from backend.access.templates import DEFAULT_ROLE_TEMPLATES


class RoleService:
    """Service for role-related operations."""
    
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
            user=user,
            room=room,
            role__permissions__code=perm_code
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
        return Role.objects.filter(room=room).prefetch_related('permissions')

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
                Role.objects
                .select_related('room')
                .prefetch_related('permissions')
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
                Participant.objects
                .select_related('role')
                .prefetch_related('role__permissions')
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
        for [role_code, data] in DEFAULT_ROLE_TEMPLATES.items():
            role = Role.objects.create(
                room=room,
                name=role_code.label,
                priority=data["priority"],
                description=data["description"],
            )
            perms = Permission.objects.filter(
                code__in=[c for c in data["permission_codes"]]
            )
            role.permissions.set(perms)

    @staticmethod
    def create_role(
        user: User,
        room: Room,
        name: str,
        description: str,
        priority: int,
        permission_ids: list[uuid.UUID],
    ) -> Role:
        """
        Create a new role in a room.
        
        Args:
            user: User creating the role (must have ROOM_ROLE_MANAGE permission)
            room: The room to create the role in
            name: Role name
            description: Role description
            priority: Role priority (0-100, higher = higher priority)
            permission_ids: List of permission IDs to assign
            
        Returns:
            The created Role instance
            
        Raises:
            PermissionException: If user doesn't have ROOM_ROLE_MANAGE permission
            ValidationException: If form validation fails
            ConflictException: If role creation conflicts
        """
        participant = RoleService.get_participant(user, room)
        
        if participant is None:
            raise PermissionException("You are not a participant of this room and cannot create roles.")
        
        if not RoleService.has_permission(user, room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
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
        
        data = {
            "name": name,
            "description": description,
            "priority": priority,
        }
        
        form = RoleForm(data=data)
        
        if not form.is_valid():
            raise FormValidationException("Invalid role data", errors=form.errors)
        
        try:
            role = form.save(commit=False)
            role.room = room
            role.save()
            
            if permission_ids:
                permissions = Permission.objects.filter(id__in=permission_ids)
                role.permissions.set(permissions)
            
        except IntegrityError as e:
            raise ConflictException("Could not create role due to a conflict.") from e

        return role

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
            user: User performing the update (must have ROOM_ROLE_MANAGE permission)
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
        participant = RoleService.get_participant(user, role.room)
        
        if participant is None:
            raise PermissionException("You are not a participant of this room and cannot update roles.")

        if not RoleService.has_permission(user, role.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        if not RoleService.can_affect_role(participant, role):
            raise PermissionException("Cannot affect roles with higher or equal priority.")
        
        data = {}
        
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if priority is not None:
            data["priority"] = priority
        
        try:
            with transaction.atomic():
                if data:
                    form = RoleForm(data=data, instance=role)
                    
                    if not form.is_valid():
                        raise FormValidationException("Invalid role data", errors=form.errors)
                    
                    form.save()
                
                if permission_ids is not None:                    
                    if not RoleService._is_valid_permission_set(participant, permission_ids):
                        raise PermissionException(
                            "Cannot assign permissions you don't have. "
                            "You can only grant permissions your role already possesses."
                        )
                    
                    permissions = Permission.objects.filter(id__in=permission_ids)
                    role.permissions.set(permissions)
                
                return role
        except IntegrityError as e:
            raise ConflictException("Could not update role due to a conflict.") from e

    @staticmethod
    def delete_role(user: User, role: Role, substitution_role: Optional[Role] = None) -> dict:
        """
        Delete a role.
        
        Args:
            user: User performing the deletion (must have ROOM_ROLE_MANAGE permission)
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

        participant = RoleService.get_participant(user, role.room)

        if participant is None:
            raise PermissionException("You are not a participant of this room and cannot delete roles.")
        
        if not RoleService.has_permission(user, role.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        if not RoleService.can_affect_role(participant, role):
            raise PermissionException("Cannot affect roles with equal or higher priority.")
        
        # Check if any participants or invites have this role
        participant_count = Participant.objects.filter(role=role).count()
        invite_count = Invite.objects.filter(role=role).count()
        
        if (participant_count > 0 or invite_count > 0) and substitution_role is None:
            raise ValidationException(
                "Cannot delete a role with active participants or invites. "
                "Provide a substitution_role to reassign them."
            )
        
        with transaction.atomic():
            participants_reassigned = 0
            invites_reassigned = 0
            
            # Reassign participants to substitution role
            if substitution_role and participant_count > 0:
                participants_reassigned = Participant.objects.filter(role=role).update(role=substitution_role)
            
            # Reassign invites to substitution role
            if substitution_role and invite_count > 0:
                invites_reassigned = Invite.objects.filter(role=role).update(role=substitution_role)
            
            role.delete()
        
        return {
            'success': True,
            'participants_reassigned': participants_reassigned,
            'invites_reassigned': invites_reassigned
        }


    @staticmethod
    def assign_permissions_to_role(
        user: User,
        role: Role,
        permission_ids: list[uuid.UUID],
    ) -> Role:
        """
        Assign permissions to a role.
        
        Args:
            user: User performing the assignment (must have ROOM_ROLE_MANAGE permission)
            role: The role to assign permissions to
            permission_ids: List of permission IDs
            
        Returns:
            The updated Role instance
            
        Raises:
            PermissionException: If user doesn't have permission, priority violation, or permission escalation attempt
        """
        participant = RoleService.get_participant(user, role.room)
        
        if participant is None:
            raise PermissionException("You are not a participant of this room and cannot manage permissions.")
        
        if not RoleService.has_permission(user, role.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        if not RoleService.can_affect_role(participant, role):
            raise PermissionException("Cannot affect roles with equal or higher priority.")
        
        if not RoleService._is_valid_permission_set(participant, permission_ids):
            raise PermissionException(
                "Cannot assign permissions you don't have. "
                "You can only grant permissions your role already possesses."
            )
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.set(permissions)
        return role

    @staticmethod
    def remove_permissions_from_role(
        user: User,
        role: Role,
        permission_ids: list[uuid.UUID],
    ) -> Role:
        """
        Remove permissions from a role.
        
        Args:
            user: User performing the removal (must have ROOM_ROLE_MANAGE permission)
            role: The role to remove permissions from
            permission_ids: List of permission IDs to remove
            
        Returns:
            The updated Role instance
            
        Raises:
            PermissionException: If user doesn't have permission or priority hierarchy violation
        """
        participant = RoleService.get_participant(user, role.room)
        
        if participant is None:
            raise PermissionException("You are not a participant of this room and cannot update roles.")
        
        if not RoleService.has_permission(user, role.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        if not RoleService.can_affect_role(participant, role):
            raise PermissionException("Cannot affect roles with higher or equal priority.")

        role.permissions.remove(*permission_ids)
        return role


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
