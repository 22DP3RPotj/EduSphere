import graphene
from backend.graphql.queries.auth_queries import AuthQuery
from backend.graphql.queries.topic_queries import TopicQuery
from backend.graphql.queries.user_queries import UserQuery
from backend.graphql.queries.message_queries import MessageQuery
from backend.graphql.queries.report_queries import ReportQuery
from backend.graphql.queries.invite_queries import InviteQuery

from backend.graphql.mutations.auth_mutations import AuthMutation
from backend.graphql.mutations.user_mutations import UserMutation
from backend.graphql.mutations.message_mutations import MessageMutation
from backend.graphql.mutations.report_mutations import ReportMutation
from backend.graphql.mutations.invite_mutations import InviteMutation

from backend.graphql.room.schema import RoomQuery, RoomMutation
from backend.graphql.access.schema import AccessQuery, AccessMutation


class Mutation(
    AuthMutation,
    UserMutation,
    RoomMutation,
    MessageMutation,
    ReportMutation,
    InviteMutation,
    AccessMutation,
    graphene.ObjectType
):
    pass


class Query(
    AuthQuery,
    TopicQuery,
    UserQuery,
    RoomQuery,
    MessageQuery,
    ReportQuery,
    InviteQuery,
    AccessQuery,
    graphene.ObjectType
):
    pass
