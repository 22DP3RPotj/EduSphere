import uuid
from typing import Optional
from django.db import IntegrityError, transaction
from django.db.models import QuerySet

from backend.core.models import Role, Room, Permission, User, Participant
from backend.core.permissions import has_permission, PermissionCode
from backend.core.forms import RoleForm
from backend.core.exceptions import FormValidationException, PermissionException, NotFoundException, ConflictException, ValidationException
from backend.core.templates import DEFAULT_ROLE_TEMPLATES


class RoleService:
    """Service for role-related operations."""

    @staticmethod
    def _get_user_role_priority(user: User, room: Room) -> int:
        """
        Get the priority of a user's role in a room.
        
        Args:
            user: The user
            room: The room
            
        Returns:
            The priority value
            
        Raises:
            ValueError: If user is not a participant
        """
        try:
            participant = Participant.objects.select_related('role').get(
                user=user,
                room=room
            )
            return participant.role.priority
        except Participant.DoesNotExist:
            raise NotFoundException("User is not a participant of this room")

    @staticmethod
    def _check_priority_can_affect(user: User, target_role: Role) -> None:
        """
        Check if a user can affect a target role based on priority hierarchy.
        Lower priority values = higher priority users (can affect higher priority values).
        
        Args:
            user: The user attempting the action
            target_role: The target role
            
        Raises:
            PermissionError: If user's priority is lower than target role's priority
        """
        user_priority = RoleService._get_user_role_priority(user, target_role.room)
        
        if user_priority <= target_role.priority:
            raise PermissionException(
                f"Cannot affect roles with higher priority. "
                f"Your priority: {user_priority}, Target priority: {target_role.priority}"
            )
            
    @staticmethod
    def create_default_roles(room: Room):
        """
        Create default roles for a room. Should be called once when the room is created.

        Args:
            room: The room
        """
        with transaction.atomic():
            for role_code, data in DEFAULT_ROLE_TEMPLATES.items():
                role = Role.objects.create(
                    room=room,
                    name=role_code.label,
                    description=data["description"],
                )
                perms = Permission.objects.filter(
                    code__in=[p.value for p in data["permissions"]]
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
            PermissionError: If user doesn't have ROOM_ROLE_MANAGE permission
            ValueError: If form validation fails
            IntegrityError: If role creation conflicts
        """
        if not has_permission(user, room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        data = {
            "name": name,
            "description": description,
            "priority": priority,
        }
        
        form = RoleForm(data=data)
        
        if not form.is_valid():
            raise FormValidationException("Invalid role data", errors=form.errors)
        
        try:
            with transaction.atomic():
                role = form.save(commit=False)
                role.room = room
                role.save()
                
                if permission_ids:
                    permissions = Permission.objects.filter(id__in=permission_ids)
                    role.permissions.set(permissions)
                
                return role
        except IntegrityError as e:
            raise ConflictException("Could not create role due to a conflict.") from e

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
            PermissionError: If user doesn't have permission or priority hierarchy violation
            ValueError: If form validation fails
            IntegrityError: If update conflicts
        """
        if not has_permission(user, role.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        # Check priority hierarchy - user must have higher priority (lower value) than target role
        RoleService._check_priority_can_affect(user, role)
        
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
                    permissions = Permission.objects.filter(id__in=permission_ids)
                    role.permissions.set(permissions)
                
                return role
        except IntegrityError as e:
            raise ConflictException("Could not update role due to a conflict.") from e

    @staticmethod
    def delete_role(user: User, role: Role, substitution_role: Optional[Role] = None) -> bool:
        """
        Delete a role.
        
        Args:
            user: User performing the deletion (must have ROOM_ROLE_MANAGE permission)
            role: The role to delete
            substitution_role: Role to reassign participants and invites to (required if role has participants/invites)
            
        Returns:
            True if deletion was successful
            
        Raises:
            PermissionError: If user doesn't have permission or priority hierarchy violation
            ValueError: If role has participants/invites but no substitution role provided
        """
        if not has_permission(user, role.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        # Check priority hierarchy - user must have higher priority (lower value) than target role
        RoleService._check_priority_can_affect(user, role)
        
        # Check if any participants or invites have this role
        participant_count = Participant.objects.filter(role=role).count()
        from backend.core.models import Invite
        invite_count = Invite.objects.filter(role=role).count()
        
        if (participant_count > 0 or invite_count > 0) and substitution_role is None:
            raise ValidationException(
                "Cannot delete a role with active participants or invites. "
                "Provide a substitution_role to reassign them."
            )
        
        with transaction.atomic():
            # Reassign participants to substitution role
            if substitution_role and participant_count > 0:
                Participant.objects.filter(role=role).update(role=substitution_role)
            
            # Reassign invites to substitution role
            if substitution_role and invite_count > 0:
                Invite.objects.filter(role=role).update(role=substitution_role)
            
            role.delete()
        
        return True

    @staticmethod
    def get_role_with_prefetch(role_id: uuid.UUID) -> Optional[Role]:
        """
        Get a role with optimized prefetch_related queries.
        
        Args:
            role_id: The ID of the role to fetch
            
        Returns:
            The Role instance or None if not found
        """
        try:
            return Role.objects.select_related('room').prefetch_related(
                'permissions'
            ).get(id=role_id)
        except Role.DoesNotExist:
            return None

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
            PermissionError: If user doesn't have permission or priority hierarchy violation
        """
        if not has_permission(user, role.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        # Check priority hierarchy
        RoleService._check_priority_can_affect(user, role)
        
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
            PermissionError: If user doesn't have permission or priority hierarchy violation
        """
        if not has_permission(user, role.room, PermissionCode.ROOM_ROLE_MANAGE):
            raise PermissionException("You don't have permission to manage roles in this room")
        
        # Check priority hierarchy
        RoleService._check_priority_can_affect(user, role)
        
        role.permissions.remove(*permission_ids)
        return role
