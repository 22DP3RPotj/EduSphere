import uuid
from typing import Any, Optional

from django.db import IntegrityError, transaction

from backend.account.models import User
from backend.access.dtos import RoleDeleteResult
from backend.access.forms import RoleForm
from backend.access.models import Participant, Role, Permission
from backend.access.templates import DEFAULT_ROLE_TEMPLATES
from backend.core.exceptions import (
    ConflictException,
    FormValidationException,
    ValidationException,
)
from backend.invite.models import Invite
from backend.room.models import Room


def create_default_roles(room: Room) -> None:
    for role_code, data in DEFAULT_ROLE_TEMPLATES.items():
        role = Role.objects.create(
            room=room,
            name=role_code.label,
            priority=data["priority"],
            description=data["description"],
        )
        perms = Permission.objects.filter(code__in=data["permission_codes"])
        role.permissions.set(perms)


def create_role(
    room: Room,
    name: str,
    description: Optional[str],
    priority: int,
    permission_ids: list[uuid.UUID],
) -> Role:
    data: dict[str, Any] = {
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


def update_role(
    role: Role,
    name: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[int] = None,
    permission_ids: Optional[list[uuid.UUID]] = None,
) -> Role:
    data: dict[str, Any] = {}

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
                    raise FormValidationException(
                        "Invalid role data", errors=form.errors
                    )

                form.save()

            if permission_ids is not None:
                permissions = Permission.objects.filter(id__in=permission_ids)
                role.permissions.set(permissions)

    except IntegrityError as e:
        raise ConflictException("Could not update role due to a conflict.") from e

    return role


def delete_role(
    role: Role, substitution_role: Optional[Role] = None
) -> RoleDeleteResult:
    with transaction.atomic():
        participants_count = Participant.objects.filter(role=role).update(
            role=substitution_role
        )
        invites_count = Invite.objects.filter(role=role).update(role=substitution_role)

        role.delete()

    return RoleDeleteResult(
        success=True,
        participants_reassigned=participants_count,
        invites_reassigned=invites_count,
    )


def assign_permissions_to_role(role: Role, permission_ids: list[uuid.UUID]) -> Role:
    permissions = Permission.objects.filter(id__in=permission_ids)
    role.permissions.set(permissions)
    return role


def remove_permissions_from_role(role: Role, permission_ids: list[uuid.UUID]) -> Role:
    if permission_ids:
        permissions = list(Permission.objects.filter(id__in=permission_ids))
        role.permissions.remove(*permissions)
    return role


def add_participant(room: Room, user: User, role: Optional[Role]) -> Participant:
    if role is not None and role.room != room:
        raise ValidationException("Role must belong to the same room.")

    if Participant.objects.filter(user=user, room=room).exists():
        raise ConflictException("User is already a participant of this room.")

    try:
        participant = Participant.objects.create(user=user, room=room, role=role)
    except IntegrityError as e:
        raise ConflictException("User is already a participant of this room.") from e

    return participant


def change_participant_role(participant: Participant, new_role: Role) -> Participant:
    if new_role.room != participant.room:
        raise ValidationException("New role must belong to the same room.")

    participant.role = new_role
    participant.save()

    return participant


def remove_participant(participant: Participant) -> bool:
    participant.delete()
    return True
