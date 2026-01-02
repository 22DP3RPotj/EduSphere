import graphene
from graphene_django.types import DjangoObjectType

from backend.room.models import Room, Topic
from backend.access.models import Participant


RoomVisibilityEnum = graphene.Enum.from_enum(Room.Visibility)


class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = (
            "id",
            "name",
        )


class RoomType(DjangoObjectType):
    participants = graphene.List("backend.graphql.access.types.ParticipantType")
    topics = graphene.List(TopicType)
    host = graphene.Field("backend.graphql.account.types.UserType", required=True)
    visibility = graphene.Field(RoomVisibilityEnum, required=True)

    class Meta:
        model = Room
        fields = (
            "id",
            "host",
            "topics",
            "name",
            "slug",
            "visibility",
            "description",
            "participants",
            "updated_at",
            "created_at",
        )
    
    def resolve_participants(self, info):
        return Participant.objects.select_related("user", "role").filter(room=self)
    
    def resolve_topics(self, info):
        return self.topics.all()