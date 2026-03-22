import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import superuser_required
from graphql import GraphQLError
from graphql_auth.queries import MeQuery

from django.db.models import QuerySet

from backend.graphql.account.types import UserType, AuthStatusType
from backend.graphql.account.filters import UserFilter
from backend.account.models import User
from backend.core.exceptions import ErrorCode


class AuthQuery(MeQuery, graphene.ObjectType):
    auth_status = graphene.Field(AuthStatusType)

    def resolve_auth_status(self, info: graphene.ResolveInfo) -> AuthStatusType:
        user = info.context.user
        if user.is_authenticated:
            return AuthStatusType(is_authenticated=True, user=user)
        return AuthStatusType(is_authenticated=False, user=None)


class UserQuery(graphene.ObjectType):
    users = graphene.List(
        UserType,
        # Search
        search=graphene.String(),
        # Boolean flags
        is_active=graphene.Boolean(),
        is_staff=graphene.Boolean(),
        is_superuser=graphene.Boolean(),
        has_avatar=graphene.Boolean(),
        has_active_ban=graphene.Boolean(),
        # Date ranges
        date_joined_after=graphene.DateTime(),
        date_joined_before=graphene.DateTime(),
        last_seen_after=graphene.DateTime(),
        last_seen_before=graphene.DateTime(),
    )
    user = graphene.Field(
        UserType,
        user_id=graphene.UUID(required=True),
    )

    @superuser_required
    def resolve_users(
        self,
        info: graphene.ResolveInfo,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_staff: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        has_avatar: Optional[bool] = None,
        has_active_ban: Optional[bool] = None,
        date_joined_after: Optional[str] = None,
        date_joined_before: Optional[str] = None,
        last_seen_after: Optional[str] = None,
        last_seen_before: Optional[str] = None,
    ) -> QuerySet[User]:
        queryset = User.objects.all().prefetch_related("hosted_rooms")
        filter_data = {
            k: v
            for k, v in {
                "search": search,
                "is_active": is_active,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
                "has_avatar": has_avatar,
                "has_active_ban": has_active_ban,
                "date_joined_after": date_joined_after,
                "date_joined_before": date_joined_before,
                "last_seen_after": last_seen_after,
                "last_seen_before": last_seen_before,
            }.items()
            if v is not None
        }
        return UserFilter(filter_data, queryset=queryset).qs

    def resolve_user(self, info: graphene.ResolveInfo, user_id: uuid.UUID) -> User:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        return user
