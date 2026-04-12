from django.db import IntegrityError

from backend.account.models import User
from backend.core.exceptions import ConflictException, FormValidationException
from backend.messaging.forms import MessageForm
from backend.messaging.models import Message
from backend.room.models import Room


def create_message(
    user: User, room: Room, body: str, parent: Message | None = None
) -> Message:
    data = {"body": body}
    form = MessageForm(data=data)

    if not form.is_valid():
        raise FormValidationException("Invalid message data", errors=form.errors)

    try:
        message = form.save(commit=False)
        message.author = user
        message.room = room
        message.parent = parent
        message.save()
    except IntegrityError as e:
        raise ConflictException("Could not create message due to a conflict.") from e

    return message


def update_message(message: Message, body: str) -> Message:
    data = {"body": body}
    form = MessageForm(data=data, instance=message)

    if not form.is_valid():
        raise FormValidationException("Invalid message data", errors=form.errors)

    try:
        updated_message = form.save(commit=False)
        if not updated_message.is_edited:
            updated_message.is_edited = True
        updated_message.save()
    except IntegrityError as e:
        raise ConflictException("Could not update message due to a conflict.") from e

    return updated_message


def delete_message(message: Message) -> bool:
    message.delete()
    return True
