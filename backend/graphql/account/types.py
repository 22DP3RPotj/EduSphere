import graphene
from graphene_django.types import DjangoObjectType

from backend.account.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "bio",
            "avatar",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
        )


class AuthStatusType(graphene.ObjectType):
    is_authenticated = graphene.Boolean(required=True)
    user = graphene.Field(UserType)
