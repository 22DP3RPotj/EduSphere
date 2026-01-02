import graphene
from graphene_django.types import DjangoObjectType

from backend.invite.models import Invite


InviteStatusEnum = graphene.Enum.from_enum(Invite.Status)

class InviteType(DjangoObjectType):
    inviter = graphene.Field("backend.graphql.account.types.UserType", required=True)
    invitee = graphene.Field("backend.graphql.account.types.UserType", required=True)
    role = graphene.Field("backend.graphql.access.types.RoleType", required=True)
    
    class Meta:
        model = Invite
        fields = (
            "id",
            "inviter",
            "invitee",
            "role",
            "token",
            "status",
            "created_at",
            "expires_at",
        )
