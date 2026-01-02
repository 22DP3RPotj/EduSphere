import graphene
from graphene_django.types import DjangoObjectType

from backend.messaging.models import Message, MessageStatus


MessageStatusEnum = graphene.Enum.from_enum(MessageStatus.Status)

class MessageType(DjangoObjectType):
    user = graphene.Field("backend.graphql.account.types.UserType", required=True)
    room = graphene.Field("backend.graphql.room.types.RoomType", required=True)
    
    class Meta:
        model = Message
        fields = (
            "id",
            "user",
            "room",
            "body",
            "is_edited",
            "created_at",
            "updated_at",
        )


class MessageStatusType(graphene.ObjectType):
    message = graphene.Field(MessageType, required=True)
    room = graphene.Field("backend.graphql.room.types.RoomType", required=True)
    status = graphene.Field(MessageStatusEnum, required=True)
    
    class Meta:
        model = MessageStatus
        fields = (
            "message",
            "room",
            "status",
            "timestamp",
        )


__all__ = [
    "MessageType",
    "MessageStatusType",
]
