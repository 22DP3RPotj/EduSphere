from datetime import datetime
from typing import Optional

import graphene
from graphene_django.types import DjangoObjectType

from backend.account.models import User
from backend.account.rules.labels import AccountPermission


class LanguageEnum(graphene.Enum):
    ENGLISH = "en"
    LATVIAN = "lv"


class UserType(DjangoObjectType):
    # Private fields
    email = graphene.String()
    is_verified = graphene.Boolean()
    verified_at = graphene.DateTime()
    # Public fields
    language = graphene.String(required=True)  # Overridden to return the ISO code

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "bio",
            "avatar",
            "language",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
            "last_login",
            "last_seen",
            "is_verified",
        )

    def resolve_email(self, info) -> Optional[str]:
        user = info.context.user

        if not user.is_authenticated:
            return None

        if user.has_perm(AccountPermission.VIEW_PRIVATE):
            return self.email

        return None

    def resolve_verified_at(self, info) -> Optional[datetime]:
        user = info.context.user

        if not user.is_authenticated:
            return None

        if user.has_perm(AccountPermission.VIEW_PRIVATE):
            return self.verified_at

        return None


class AuthStatusType(graphene.ObjectType):
    is_authenticated = graphene.Boolean(required=True)
    user = graphene.Field(UserType)
