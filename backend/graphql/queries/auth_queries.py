import graphene
from graphql_jwt.decorators import login_required

from backend.graphql.types import UserType, AuthStatusType
from backend.core.models import User


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
    