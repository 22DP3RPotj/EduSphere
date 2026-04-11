import graphene
from graphene_django.types import DjangoObjectType

from backend.invite.models import Invite


class InviteStatusEnum(graphene.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class InviteType(DjangoObjectType):
    inviter = graphene.Field("backend.graphql.account.types.UserType", required=True)
    invitee = graphene.Field("backend.graphql.account.types.UserType", required=True)
    room = graphene.Field("backend.graphql.room.types.RoomType", required=True)
    role = graphene.Field("backend.graphql.access.types.RoleType")
    status = graphene.Field(InviteStatusEnum, required=True)

    class Meta:
        model = Invite
        fields = (
            "id",
            "inviter",
            "invitee",
            "room",
            "role",
            "token",
            "status",
            "created_at",
            "expires_at",
        )

    def resolve_status(self, info: graphene.ResolveInfo):
        return str(self.status)
