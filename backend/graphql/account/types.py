from typing import Optional

import graphene
from graphene_django.types import DjangoObjectType

from backend.account.models import User


class UserType(DjangoObjectType):
    # Private fields
    email = graphene.String()

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
            "last_login",
            "last_seen",
        )

    def resolve_email(self, info) -> Optional[str]:
        user = info.context.user

        if not user.is_authenticated:
            return None

        if user.is_superuser or user.id == self.id:
            return self.email

        return None


class AuthStatusType(graphene.ObjectType):
    is_authenticated = graphene.Boolean(required=True)
    user = graphene.Field(UserType)
