import graphene
from .auth_mutations import AuthMutation
from .user_mutations import UserMutation
from .room_mutations import RoomMutation
from .message_mutations import MessageMutation
from .report_mutations import ReportMutation
from .invite_mutations import InviteMutation
from .role_mutations import RoleMutation
from .participant_mutations import ParticipantMutation


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
