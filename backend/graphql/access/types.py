import graphene
from graphene_django.types import DjangoObjectType
from graphene_pydantic import PydanticObjectType

from backend.access.models import Participant, Role, Permission
from backend.graphql.account.types import UserType
from backend.access.dtos import RoleDeleteResult


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

    class Meta:
        model = Participant
        fields = (
            "id",
            "user",
            "role",
            "joined_at",
        )


class RoleDeleteType(PydanticObjectType):
    class Meta:
        model = RoleDeleteResult
