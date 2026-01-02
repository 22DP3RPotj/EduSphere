import graphene

from backend.graphql.room.schema import RoomQueries, RoomMutations
from backend.graphql.invite.schema import InviteQueries, InviteMutations
from backend.graphql.access.schema import AccessQueries, AccessMutations
from backend.graphql.moderation.schema import ModerationQueries, ModerationMutations
from backend.graphql.messaging.schema import MessagingQueries, MessagingMutation
from backend.graphql.account.schema import AccountQueries, AccountMutations

class Mutation(
    AccountMutations,
    RoomMutations,
    InviteMutations,
    MessagingMutation,
    AccessMutations,
    ModerationMutations,
    graphene.ObjectType
):
    pass


class Query(
    AccountQueries,
    RoomQueries,
    InviteQueries,
    MessagingQueries,
    AccessQueries,
    ModerationQueries,
    graphene.ObjectType
):
    pass
