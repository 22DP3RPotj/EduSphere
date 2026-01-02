import graphene
from graphene_django.types import DjangoObjectType

from backend.messaging.models import Message


class MessageType(DjangoObjectType):
    user = graphene.Field("backend.graphql.types.UserType", required=True)
    room = graphene.Field("backend.graphql.room.types.RoomType")
    
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
