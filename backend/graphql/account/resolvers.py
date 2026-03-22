import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import superuser_required
from graphql import GraphQLError
from graphql_auth.queries import MeQuery

from django.db.models import QuerySet

from backend.graphql.account.filters import UserFilter
from backend.graphql.account.types import UserType, AuthStatusType
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
    users = graphene.List(UserType, search=graphene.String())
    user = graphene.Field(
        UserType,
        user_id=graphene.UUID(required=True),
    )

    @superuser_required
    def resolve_users(
        self, info: graphene.ResolveInfo, search: Optional[str] = None
    ) -> QuerySet[User]:
        queryset = User.objects.all().prefetch_related("hosted_rooms")

        filter_data = {"search": search} if search else {}
        return UserFilter(filter_data, queryset=queryset).qs

    def resolve_user(self, info: graphene.ResolveInfo, user_id: uuid.UUID) -> User:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        return user
