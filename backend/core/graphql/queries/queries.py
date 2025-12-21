import graphene
from .auth_queries import AuthQuery
from .topic_queries import TopicQuery
from .user_queries import UserQuery
from .room_queries import RoomQuery
from .message_queries import MessageQuery
from .report_queries import ReportQuery
from .inivte_queries import InviteQuery
from .role_queries import RoleQuery


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
