import uuid
import graphene
from graphql import GraphQLError

from django.db.models import QuerySet

from backend.core.exceptions import ErrorCode
from backend.account.models import User
from backend.messaging.models import Message
from backend.room.models import Room
from backend.access.models import Participant
from backend.graphql.messaging.types import MessageType


class MessageQuery(graphene.ObjectType):
    messages = graphene.List(
        MessageType,
        room_id=graphene.UUID(required=True)
    )
    messages_by_user = graphene.List(
        MessageType,
        user_slug=graphene.String(required=True),   
    )
    
    def resolve_messages(self, info: graphene.ResolveInfo, room_id: uuid.UUID) -> QuerySet[Message]:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        if not Participant.objects.filter(user=info.context.user, room=room).exists():
            raise GraphQLError("Not a participant", extensions={"code": ErrorCode.PERMISSION_DENIED})

        return room.message_set.select_related('user').order_by('created_at')
    
    def resolve_messages_by_user(self, info: graphene.ResolveInfo, user_slug: str) -> QuerySet[Message]:
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        return user.message_set.select_related('room', 'room__host').order_by('-created_at')
