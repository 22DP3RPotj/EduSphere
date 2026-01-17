import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import superuser_required

from backend.account.models import UserHistory
from backend.room.models import RoomHistory
from backend.invite.models import InviteHistory

from backend.graphql.audit.types import UserAuditType, RoomAuditType, InviteAuditType
from backend.graphql.audit.filters import (
    UserAuditFilter,
    RoomAuditFilter,
    InviteAuditFilter,
)


class AuditQuery(graphene.ObjectType):
    user_audits = DjangoFilterConnectionField(
        UserAuditType,
        filterset_class=UserAuditFilter,
    )

    room_audits = DjangoFilterConnectionField(
        RoomAuditType,
        filterset_class=RoomAuditFilter,
    )

    invite_audits = DjangoFilterConnectionField(
        InviteAuditType,
        filterset_class=InviteAuditFilter,
    )

    @superuser_required
    def resolve_user_audits(self, info, **kwargs):
        return UserHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_room_audits(self, info, **kwargs):
        return RoomHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_invite_audits(self, info, **kwargs):
        return InviteHistory.objects.all().order_by("-pgh_created_at")
