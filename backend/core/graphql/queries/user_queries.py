import graphene
from typing import Optional
from graphql import GraphQLError
from graphql_jwt.decorators import superuser_required

from django.db.models import Q, QuerySet

from backend.core.graphql.types import UserType
from backend.core.models import User


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
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        return user
