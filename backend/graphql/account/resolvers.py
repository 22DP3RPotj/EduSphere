import graphene
from typing import Optional
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.db.models import Q, QuerySet

from backend.graphql.account.types import UserType, AuthStatusType
from backend.account.models import User
from backend.core.exceptions import ErrorCode


class AuthQuery(graphene.ObjectType):
    auth_status = graphene.Field(AuthStatusType)
    me = graphene.Field(UserType)
    
    @login_required
    def resolve_me(self, info: graphene.ResolveInfo) -> User:
        return info.context.user
    
    def resolve_auth_status(self, info: graphene.ResolveInfo) -> AuthStatusType:
        user = info.context.user
        if user.is_authenticated:
            return AuthStatusType(is_authenticated=True, user=user)
        return AuthStatusType(is_authenticated=False, user=None)


class UserQuery(graphene.ObjectType):
    users = graphene.List(
        UserType,
        search=graphene.String()
    )
    user = graphene.Field(
        UserType,
        user_slug=graphene.String(required=True),
    )
    
    @superuser_required
    def resolve_users(self, info: graphene.ResolveInfo, search: Optional[str] = None) -> QuerySet[User]:
        queryset = User.objects.all().prefetch_related('hosted_rooms')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(name__icontains=search)
            )
        return queryset
    
    def resolve_user(self, info: graphene.ResolveInfo, user_slug: str) -> User:
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": ErrorCode.NOT_FOUND})

        return user
