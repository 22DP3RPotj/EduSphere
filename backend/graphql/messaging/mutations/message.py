import graphene
import uuid
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.graphql.messaging.types import MessageType
from backend.messaging.models import Message
from backend.room.models import Room
from backend.messaging.services import MessageService
from backend.core.exceptions import (
    PermissionException,
    FormValidationException,
    ConflictException,
    ErrorCode,
)


class CreateMessage(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        body = graphene.String(required=True)

    message = graphene.Field(MessageType)

    @login_required
    def mutate(self, info: graphene.ResolveInfo, room_id: uuid.UUID, body: str):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            message = MessageService.create_message(
                user=info.context.user, room=room, body=body
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except (FormValidationException, ConflictException) as e:
            raise GraphQLError(
                str(e),
                extensions={"code": e.code, "errors": getattr(e, "errors", None)},
            )

        return CreateMessage(message=message)


class DeleteMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info: graphene.ResolveInfo, message_id: uuid.UUID):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError(
                "Message not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            success = MessageService.delete_message(
                user=info.context.user, message=message
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return DeleteMessage(success=success)


class UpdateMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)
        body = graphene.String(required=True)

    message = graphene.Field(MessageType)

    @login_required
    def mutate(self, info: graphene.ResolveInfo, message_id: uuid.UUID, body: str):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError(
                "Message not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            message = MessageService.update_message(
                user=info.context.user, message=message, body=body
            )
        except (PermissionException, ConflictException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})

        return UpdateMessage(message=message)
