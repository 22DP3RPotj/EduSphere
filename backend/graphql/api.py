import graphene
from backend.graphql.queries.auth_queries import AuthQuery
from backend.graphql.queries.topic_queries import TopicQuery
from backend.graphql.queries.user_queries import UserQuery
from backend.graphql.queries.room_queries import RoomQuery
from backend.graphql.queries.message_queries import MessageQuery
from backend.graphql.queries.report_queries import ReportQuery
from backend.graphql.queries.invite_queries import InviteQuery
from backend.graphql.queries.role_queries import RoleQuery

from backend.graphql.mutations.auth_mutations import AuthMutation
from backend.graphql.mutations.user_mutations import UserMutation
from backend.graphql.mutations.room_mutations import RoomMutation
from backend.graphql.mutations.message_mutations import MessageMutation
from backend.graphql.mutations.report_mutations import ReportMutation
from backend.graphql.mutations.invite_mutations import InviteMutation
from backend.graphql.mutations.role_mutations import RoleMutation
from backend.graphql.mutations.participant_mutations import ParticipantMutation


class Mutation(
    AuthMutation,
    UserMutation,
    RoomMutation,
    MessageMutation,
    ReportMutation,
    InviteMutation,
    RoleMutation,
    ParticipantMutation,
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
    RoleQuery,
    graphene.ObjectType
):
    pass
