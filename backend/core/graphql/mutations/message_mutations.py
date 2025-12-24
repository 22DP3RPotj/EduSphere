import graphene
import uuid
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.core.graphql.types import MessageType
from backend.core.models import Message
from backend.core.services import MessageService
from backend.core.exceptions import (
    PermissionException,
    FormValidationException,
    ConflictException,
    ErrorCode
)


class DeleteMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info: graphene.ResolveInfo, message_id: uuid.UUID):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError("Message not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            success = MessageService.delete_message(
                user=info.context.user,
                message=message
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
            raise GraphQLError("Message not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            message = MessageService.update_message(
                user=info.context.user,
                message=message,
                body=body
            )
        except (PermissionException, ConflictException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})
    
        return UpdateMessage(message=message)


class MessageMutation(graphene.ObjectType):
    delete_message = DeleteMessage.Field()
    update_message = UpdateMessage.Field()
