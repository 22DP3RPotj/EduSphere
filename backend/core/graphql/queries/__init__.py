import graphene
from .auth import AuthQuery
from .topic import TopicQuery
from .user import UserQuery
from .room import RoomQuery
from .message import MessageQuery


class Query(
    AuthQuery,
    TopicQuery,
    UserQuery,
    RoomQuery,
    MessageQuery,
    graphene.ObjectType
):
    pass
