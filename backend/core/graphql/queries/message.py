import graphene
from graphql import GraphQLError
from backend.core.graphql.types import MessageType
from backend.core.models import Room, User


class MessageQuery(graphene.ObjectType):
    messages = graphene.List(
        MessageType,
        host_slug=graphene.String(required=True),
        room_slug=graphene.String(required=True)
    )
    messages_by_user = graphene.List(
        MessageType,
        user_slug=graphene.String(required=True),   
    )
    
    def resolve_messages(self, info, host_slug, room_slug):
        try:
            room = Room.objects.get(
                host__username=host_slug,
                slug=room_slug
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        if not room.participants.filter(id=info.context.user.id).exists():
            raise GraphQLError("Not a participant", extensions={"code": "PERMISSION_DENIED"})

        return room.message_set.all().order_by('created')
    
    def resolve_messages_by_user(self, info, user_slug):
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        return user.message_set.all().order_by('-created')