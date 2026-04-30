import graphene

from backend.graphql.access.schema import AccessMutations, AccessQueries
from backend.graphql.account.schema import AccountMutations, AccountQueries
from backend.graphql.audit.schema import AuditQueries
from backend.graphql.invite.schema import InviteMutations, InviteQueries
from backend.graphql.messaging.schema import MessagingMutation, MessagingQueries
from backend.graphql.moderation.schema import ModerationMutations, ModerationQueries
from backend.graphql.room.schema import RoomMutations, RoomQueries


class Mutation(
    AccountMutations,
    RoomMutations,
    InviteMutations,
    MessagingMutation,
    AccessMutations,
    ModerationMutations,
    graphene.ObjectType,
):
    pass


class Query(
    AccountQueries,
    RoomQueries,
    InviteQueries,
    MessagingQueries,
    AccessQueries,
    ModerationQueries,
    AuditQueries,
    graphene.ObjectType,
):
    pass
