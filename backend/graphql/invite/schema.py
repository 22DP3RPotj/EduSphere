import graphene

from .resolvers import InviteQuery

from .mutations.invite import (
    SendInvite,
    AcceptInvite,
    DeclineInvite,
    CancelInvite,
)


class InviteQueries(InviteQuery,graphene.ObjectType):
    pass


class InviteMutations(graphene.ObjectType):
    send_invite = SendInvite.Field()
    accept_invite = AcceptInvite.Field()
    decline_invite = DeclineInvite.Field()
    cancel_invite = CancelInvite.Field()
    

__all__ = [
    "InviteQueries",
    "InviteMutations",
]
