import graphene
from graphene_django.types import DjangoObjectType

from backend.room.models import Room, Topic
from backend.access.models import Participant


class RoomVisibilityEnum(graphene.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = (
            "id",
            "name",
        )


class RoomType(DjangoObjectType):
    participants = graphene.List(
        "backend.graphql.access.types.ParticipantType", required=True
    )
    topics = graphene.List(TopicType, required=True)
    host = graphene.Field("backend.graphql.account.types.UserType", required=True)
    visibility = graphene.Field(RoomVisibilityEnum, required=True)

    class Meta:
        model = Room
        fields = (
            "id",
            "host",
            "topics",
            "name",
            "visibility",
            "description",
            "participants",
            "updated_at",
            "created_at",
        )

    def resolve_participants(self, info):
        return Participant.objects.select_related("user", "role").filter(room=self)

    def resolve_visibility(self, info: graphene.ResolveInfo):
        return str(self.visibility)

    def resolve_topics(self, info):
        return self.topics.all()
