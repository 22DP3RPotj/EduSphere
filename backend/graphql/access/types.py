import graphene
from graphene_django.types import DjangoObjectType

from backend.core.models import Room
from backend.access.models import Participant, Role, Permission
from backend.graphql.types import UserType, TopicType, RoomVisibilityEnum

class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = (
            "id",
            "code",
            "description"
        )
        

class RoleType(DjangoObjectType):
    permissions = graphene.List(PermissionType)
    
    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "permissions",
        )


# TODO: Use real id
class ParticipantType(DjangoObjectType):
    user = graphene.Field(UserType, required=True)
    role = graphene.Field(RoleType)
    username = graphene.String()
    avatar = graphene.String()

    class Meta:
        model = Participant
        fields = (
            "id",
            "user",
            "role",
            "joined_at",
        )
    
    def resolve_username(self, info):
        return self.user.username
    
    def resolve_avatar(self, info):
        return self.user.avatar

# TODO: Return UserType instead of ParticipantType
class RoomType(DjangoObjectType):
    participants = graphene.List(ParticipantType)
    topics = graphene.List(TopicType)
    host = graphene.Field(UserType, required=True)
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
    
