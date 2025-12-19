import graphene
from .auth import AuthMutation
from .user import UserMutation
from .room import RoomMutation
from .message import MessageMutation
from .report import ReportMutation
from .invite import InviteMutation
from .role import RoleMutation

class Mutation(
    AuthMutation,
    UserMutation,
    RoomMutation,
    MessageMutation,
    ReportMutation,
    InviteMutation,
    RoleMutation,
    graphene.ObjectType
):
    pass
