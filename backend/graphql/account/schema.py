import graphene

from .resolvers import AuthQuery, UserQuery
from .mutations.user import (
    Register,
    UpdateUser,
)
from .mutations.auth import AuthMutation
from .mutations.moderation import BanUsers, UnbanUsers, PromoteUsers, DemoteUsers


class AccountQueries(AuthQuery, UserQuery, graphene.ObjectType):
    pass


class AccountMutations(AuthMutation, graphene.ObjectType):
    register = Register.Field()
    update_user = UpdateUser.Field()
    ban_users = BanUsers.Field()
    unban_users = UnbanUsers.Field()
    promote_users = PromoteUsers.Field()
    demote_users = DemoteUsers.Field()
