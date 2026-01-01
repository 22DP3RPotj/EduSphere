import graphene

from .resolvers import InviteQuery

from .mutations.invite import (
    SendInvite,
    AcceptInvite,
    DeclineInvite,
    CancelInvite,
)

# TODO: not do that
class InviteQuery(InviteQuery,graphene.ObjectType):
    pass


class InviteMutation(graphene.ObjectType):
    send_invite = SendInvite.Field()
    accept_invite = AcceptInvite.Field()
    decline_invite = DeclineInvite.Field()
    cancel_invite = CancelInvite.Field()
    