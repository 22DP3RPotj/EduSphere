import graphene
from .auth import AuthMutation
from .user import UserMutation
from .room import RoomMutation
from .message import MessageMutation
from .report import ReportMutation


class Mutation(
    AuthMutation,
    UserMutation,
    RoomMutation,
    MessageMutation,
    ReportMutation,
    graphene.ObjectType
):
    pass
