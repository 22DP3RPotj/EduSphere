import graphene
from .auth import AuthMutation
from .user import UserMutation
from .room import RoomMutation
from .message import MessageMutation


class Mutation(
    AuthMutation,
    UserMutation,
    RoomMutation,
    MessageMutation,
    graphene.ObjectType
):
    pass
