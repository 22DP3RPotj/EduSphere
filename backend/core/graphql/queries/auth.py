import graphene
from graphql_jwt.decorators import login_required
from backend.core.graphql.types import UserType, AuthStatusType


class AuthQuery(graphene.ObjectType):
    auth_status = graphene.Field(AuthStatusType)
    me = graphene.Field(UserType)
    
    @login_required
    def resolve_me(self, info):
        return info.context.user
    
    def resolve_auth_status(self, info):
        user = info.context.user
        if user.is_authenticated:
            return AuthStatusType(is_authenticated=True, user=user)
        return AuthStatusType(is_authenticated=False, user=None)
    