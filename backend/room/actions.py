from typing import Optional

from django.db import IntegrityError, transaction

from backend.account.models import User
from backend.access.enums import RoleCode
from backend.access.models import Participant
from backend.access.services import RoleService
from backend.core.exceptions import ConflictException, FormValidationException
from backend.room.choices import VisibilityChoices
from backend.room.forms import RoomForm
from backend.room.models import Room, Topic


def create_room(
    *,
    user: User,
    name: str,
    description: str,
    topic_names: list[str],
    visibility: Optional[VisibilityChoices] = None,
) -> Room:
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
        room.update_default_role(member_role)

        owner_role = room.roles.get(name=RoleCode.OWNER.label)

        try:
            Participant.objects.create(user=user, room=room, role=owner_role)
        except IntegrityError as e:
            raise ConflictException("Could not create room due to a conflict.") from e

    return room


def update_room(
    *,
    room: Room,
    name: Optional[str] = None,
    description: Optional[str] = None,
    visibility: Optional[VisibilityChoices] = None,
    topic_names: Optional[list[str]] = None,
) -> Room:
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
                room.update_visibility(visibility)
    except IntegrityError as e:
        raise ConflictException("Could not update room due to a conflict.") from e

    return room


def delete_room(room: Room) -> bool:
    room.delete()
    return True


def join_room(user: User, room: Room) -> Room:
    Participant.objects.create(user=user, room=room, role=room.default_role)

    return room


def leave_room(participant: Participant) -> bool:
    participant.delete()
    return True
