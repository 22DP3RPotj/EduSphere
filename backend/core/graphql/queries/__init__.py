import graphene
from .auth import AuthQuery
from .topic import TopicQuery
from .user import UserQuery
from .room import RoomQuery
from .message import MessageQuery
from .report import ReportQuery
from .inivte import InviteQuery
from .role import RoleQuery

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
