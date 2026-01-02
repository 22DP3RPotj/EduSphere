import graphene
from backend.graphql.queries.auth_queries import AuthQuery
from backend.graphql.queries.user_queries import UserQuery

from backend.graphql.mutations.auth_mutations import AuthMutation
from backend.graphql.mutations.user_mutations import UserMutation

from backend.graphql.room.schema import RoomQueries, RoomMutations
from backend.graphql.invite.schema import InviteQueries, InviteMutations
from backend.graphql.access.schema import AccessQueries, AccessMutations
from backend.graphql.moderation.schema import ModerationQueries, ModerationMutations
from backend.graphql.messaging.schema import MessagingQueries, MessagingMutation


class Mutation(
    RoomMutations,
    InviteMutations,
    MessagingMutation,
    AccessMutations,
    ModerationMutations,
    AuthMutation,
    UserMutation,
    graphene.ObjectType
):
    pass


class Query(
    AuthQuery,
    RoomQueries,
    InviteQueries,
    MessagingQueries,
    AccessQueries,
    ModerationQueries,
    UserQuery,
    graphene.ObjectType
):
    pass
