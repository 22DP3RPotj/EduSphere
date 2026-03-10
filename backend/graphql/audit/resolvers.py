import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import superuser_required

from backend.account.models import UserBanHistory, UserHistory
from backend.moderation.models import (
    ModerationActionHistory,
    ModerationCaseHistory,
    ReportHistory,
)
from backend.room.models import RoomHistory
from backend.invite.models import InviteHistory, InviteLinkHistory

from backend.graphql.audit.types import (
    ModerationActionAuditType,
    ModerationCaseAuditType,
    ReportAuditType,
    UserAuditType,
    RoomAuditType,
    InviteAuditType,
    InviteLinkAuditType,
    UserBanAuditType,
)
from backend.graphql.audit.filters import (
    InviteLinkAuditFilter,
    ModerationActionAuditFilter,
    ModerationCaseAuditFilter,
    ReportAuditFilter,
    UserAuditFilter,
    RoomAuditFilter,
    InviteAuditFilter,
    UserBanAuditFilter,
)


class AuditQuery(graphene.ObjectType):
    user_audits = DjangoFilterConnectionField(
        UserAuditType,
        filterset_class=UserAuditFilter,
    )

    user_ban_audits = DjangoFilterConnectionField(
        UserBanAuditType,
        filterset_class=UserBanAuditFilter,
    )

    room_audits = DjangoFilterConnectionField(
        RoomAuditType,
        filterset_class=RoomAuditFilter,
    )

    invite_audits = DjangoFilterConnectionField(
        InviteAuditType,
        filterset_class=InviteAuditFilter,
    )

    invite_link_audits = DjangoFilterConnectionField(
        InviteLinkAuditType,
        filterset_class=InviteLinkAuditFilter,
    )

    report_audits = DjangoFilterConnectionField(
        ReportAuditType,
        filterset_class=ReportAuditFilter,
    )

    moderation_action_audits = DjangoFilterConnectionField(
        ModerationActionAuditType,
        filterset_class=ModerationActionAuditFilter,
    )

    moderation_case_audits = DjangoFilterConnectionField(
        ModerationCaseAuditType,
        filterset_class=ModerationCaseAuditFilter,
    )

    @superuser_required
    def resolve_user_audits(self, info, **kwargs):
        return UserHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_user_ban_audits(self, info, **kwargs):
        return UserBanHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_room_audits(self, info, **kwargs):
        return RoomHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_invite_audits(self, info, **kwargs):
        return InviteHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_invite_link_audits(self, info, **kwargs):
        return InviteLinkHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_report_audits(self, info, **kwargs):
        return ReportHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_moderation_action_audits(self, info, **kwargs):
        return ModerationActionHistory.objects.all().order_by("-pgh_created_at")

    @superuser_required
    def resolve_moderation_case_audits(self, info, **kwargs):
        return ModerationCaseHistory.objects.all().order_by("-pgh_created_at")
