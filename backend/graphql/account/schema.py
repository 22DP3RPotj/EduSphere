import graphene

from .resolvers import (
    AuthQuery,
    UserQuery
)
from .mutations.user import (
    RegisterUser,
    UpdateUser,
    UpdateUserActiveStatus,
    UpdateUserStaffStatus,
)
from .mutations.auth import AuthMutation


class AccountQueries(AuthQuery, UserQuery, graphene.ObjectType):
    pass


class AccountMutations(AuthMutation, graphene.ObjectType):
    register_user = RegisterUser.Field()
    update_user = UpdateUser.Field()
    update_user_active_status = UpdateUserActiveStatus.Field()
    update_user_staff_status = UpdateUserStaffStatus.Field()


__all__ = [
    "AccountQueries",
    "AccountMutations",
]
