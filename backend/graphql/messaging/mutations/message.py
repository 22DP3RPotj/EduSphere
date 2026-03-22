import graphene
import uuid
from typing import Any, Optional, Self
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.graphql.mutations import BaseMutation
from backend.graphql.messaging.types import MessageType
from backend.messaging.models import Message
from backend.room.models import Room
from backend.messaging.services import MessageService
from backend.core.exceptions import ErrorCode


class CreateMessage(BaseMutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        body = graphene.String(required=True)

    message = graphene.Field(MessageType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        body: str,
    ) -> Self:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        message = MessageService.create_message(
            user=info.context.user, room=room, body=body
        )

        return cls(message=message)


class DeleteMessage(BaseMutation):
    class Arguments:
        message_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @classmethod
    @login_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, message_id: uuid.UUID
    ) -> Self:
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError(
                "Message not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        success = MessageService.delete_message(user=info.context.user, message=message)

        return cls(success=success)


class UpdateMessage(BaseMutation):
    class Arguments:
        message_id = graphene.UUID(required=True)
        body = graphene.String(required=True)

    message = graphene.Field(MessageType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        message_id: uuid.UUID,
        body: str,
    ) -> Self:
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError(
                "Message not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        message = MessageService.update_message(
            user=info.context.user, message=message, body=body
        )

        return cls(message=message)
