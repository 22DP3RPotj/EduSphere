import graphene
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
    user_audits = graphene.List(
        UserAuditType,
        date_from=graphene.Date(),
        date_to=graphene.Date(),
        action=graphene.String(),
        target_id=graphene.UUID(),
        username=graphene.String(),
        email=graphene.String(),
        limit=graphene.Int(default_value=50),
    )

    room_audits = graphene.List(
        RoomAuditType,
        date_from=graphene.Date(),
        date_to=graphene.Date(),
        action=graphene.String(),
        target_id=graphene.UUID(),
        name=graphene.String(),
        limit=graphene.Int(default_value=50),
    )

    invite_audits = graphene.List(
        InviteAuditType,
        date_from=graphene.Date(),
        date_to=graphene.Date(),
        action=graphene.String(),
        target_id=graphene.UUID(),
        status=graphene.String(),
        limit=graphene.Int(default_value=50),
    )

    @superuser_required
    def resolve_user_audits(self, info, limit=50, **kwargs):
        qs = UserHistory.objects.all().order_by("-pgh_created_at")
        return UserAuditFilter(kwargs, queryset=qs).qs[:limit]

    @superuser_required
    def resolve_room_audits(self, info, limit=50, **kwargs):
        qs = RoomHistory.objects.all().order_by("-pgh_created_at")
        return RoomAuditFilter(kwargs, queryset=qs).qs[:limit]

    @superuser_required
    def resolve_invite_audits(self, info, limit=50, **kwargs):
        qs = InviteHistory.objects.all().order_by("-pgh_created_at")
        return InviteAuditFilter(kwargs, queryset=qs).qs[:limit]
