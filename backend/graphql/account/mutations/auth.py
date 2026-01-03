import graphene
import graphql_jwt

from backend.graphql.account.types import UserType


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user, success=True)
    

class AuthMutation(graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    delete_token  = graphql_jwt.DeleteJSONWebTokenCookie.Field()
    delete_refresh_token = graphql_jwt.DeleteRefreshTokenCookie.Field()
