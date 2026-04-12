import graphene
from graphene_django.types import DjangoObjectType

from backend.messaging.models import Message, MessageStatus


class MessageStatusEnum(graphene.Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    SEEN = "SEEN"


class StatusSummaryType(graphene.ObjectType):
    delivered = graphene.Int(required=True)
    seen = graphene.Int(required=True)


class MessageType(DjangoObjectType):
    author = graphene.Field("backend.graphql.account.types.UserType", required=True)
    room = graphene.Field("backend.graphql.room.types.RoomType", required=True)
    parent = graphene.Field("backend.graphql.messaging.types.MessageType")
    status_summary = graphene.Field(StatusSummaryType)

    class Meta:
        model = Message
        fields = (
            "id",
            "author",
            "room",
            "parent",
            "body",
            "is_edited",
            "created_at",
            "updated_at",
        )

    def resolve_status_summary(self, info):
        if hasattr(self, "_status_delivered") and hasattr(self, "_status_seen"):
            return StatusSummaryType(
                delivered=self._status_delivered, seen=self._status_seen
            )
        return None


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
