import graphene
import uuid
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.core.graphql.types import MessageType
from backend.core.graphql.utils import format_form_errors
from backend.core.models import Message, PermissionCode
from backend.core.forms import MessageForm
from backend.core.services import RoleService


class DeleteMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info: graphene.ResolveInfo, message_id: uuid.UUID):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError("Message not found", extensions={"code": "NOT_FOUND"})
        
        if message.user != info.context.user and not RoleService.has_permission(info.context.user, message.room, PermissionCode.ROOM_DELETE_MESSAGE):
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        message.delete()
        return DeleteMessage(success=True)
    
    
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
            raise GraphQLError("Message not found", extensions={"code": "NOT_FOUND"})
        
        if message.user != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        data = {
            "body": body,
        }
        form = MessageForm(data=data, instance=message)
        
        
        if not form.is_valid():
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})
        
        message = form.save(commit=False)
        if not message.edited:
            message.edited = True
        message.save()
        return UpdateMessage(message=message)
    
    
class MessageMutation(graphene.ObjectType):
    delete_message = DeleteMessage.Field()
    update_message = UpdateMessage.Field()
