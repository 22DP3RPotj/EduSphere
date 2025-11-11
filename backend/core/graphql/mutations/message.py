import graphene
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.core.graphql.types import MessageType

from backend.core.models import Message


class DeleteMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError("Message not found", extensions={"code": "NOT_FOUND"})
        
        if message.user != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        message.delete()
        return DeleteMessage(success=True)
    
    
class UpdateMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)
        body = graphene.String(required=True)

    message = graphene.Field(MessageType)

    @login_required
    def mutate(self, info, message_id, body):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError("Message not found", extensions={"code": "NOT_FOUND"})
        
        if message.user != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        message.update(body)
        return UpdateMessage(message=message)
    
    
class MessageMutation(graphene.ObjectType):
    delete_message = DeleteMessage.Field()
    update_message = UpdateMessage.Field()
