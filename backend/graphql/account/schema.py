import graphene

from .mutations.auth import AuthMutation
from .mutations.moderation import (
    BanUser,
    BanUsers,
    DemoteUser,
    DemoteUsers,
    PromoteUser,
    PromoteUsers,
    UnbanUser,
    UnbanUsers,
)
from .mutations.user import (
    Register,
    UpdateUser,
)
from .resolvers import AuthQuery, UserQuery


class AccountQueries(AuthQuery, UserQuery, graphene.ObjectType):
    pass


class AccountMutations(AuthMutation, graphene.ObjectType):
    register = Register.Field()
    update_user = UpdateUser.Field()
    ban_users = BanUsers.Field()
    ban_user = BanUser.Field()
    unban_users = UnbanUsers.Field()
    unban_user = UnbanUser.Field()
    promote_users = PromoteUsers.Field()
    demote_users = DemoteUsers.Field()
    promote_user = PromoteUser.Field()
    demote_user = DemoteUser.Field()
