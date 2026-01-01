import graphene
from backend.graphql.queries.auth_queries import AuthQuery
from backend.graphql.queries.user_queries import UserQuery
from backend.graphql.queries.message_queries import MessageQuery

from backend.graphql.mutations.auth_mutations import AuthMutation
from backend.graphql.mutations.user_mutations import UserMutation
from backend.graphql.mutations.message_mutations import MessageMutation

from backend.graphql.room.schema import RoomQueries, RoomMutations
from backend.graphql.invite.schema import InviteQueries, InviteMutations
from backend.graphql.access.schema import AccessQueries, AccessMutations
from backend.graphql.moderation.schema import ModerationQueries, ModerationMutations


class Mutation(
    RoomMutations,
    InviteMutations,
    AccessMutations,
    ModerationMutations,
    AuthMutation,
    UserMutation,
    MessageMutation,
    graphene.ObjectType
):
    pass


class Query(
    AuthQuery,
    InviteQueries,
    AccessQueries,
    ModerationQueries,
    UserQuery,
    RoomQueries,
    MessageQuery,
    graphene.ObjectType
):
    pass
