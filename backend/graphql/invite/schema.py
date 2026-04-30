import graphene

from .mutations.invite import (
    AcceptInvite,
    CancelInvite,
    DeclineInvite,
    ResendInvite,
    SendInvite,
)
from .resolvers import InviteQuery


class InviteQueries(InviteQuery, graphene.ObjectType):
    pass


class InviteMutations(graphene.ObjectType):
    send_invite = SendInvite.Field()
    accept_invite = AcceptInvite.Field()
    decline_invite = DeclineInvite.Field()
    cancel_invite = CancelInvite.Field()
    resend_invite = ResendInvite.Field()
