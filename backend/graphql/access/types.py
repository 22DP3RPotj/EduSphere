import graphene
from graphene_django.types import DjangoObjectType

from backend.access.models import Participant, Role, Permission
from backend.graphql.account.types import UserType


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = ("id", "code", "description")


class RoleType(DjangoObjectType):
    permissions = graphene.List(PermissionType, required=True)

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "permissions",
        )


class ParticipantType(DjangoObjectType):
    user = graphene.Field(UserType, required=True)
    role = graphene.Field(RoleType)
    username = graphene.String(required=True)
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
