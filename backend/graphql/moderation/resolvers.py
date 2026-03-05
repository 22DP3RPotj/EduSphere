import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from backend.account.models import User
from backend.core.exceptions import ErrorCode
from backend.graphql.moderation.types import (
    ReportType,
    ReportReasonType,
    ReportStatusEnum,
    ReportTargetTypeEnum,
)
from backend.moderation.choices import ReportStatus
from backend.moderation.models import Report, ReportReason
from backend.room.models import Room


class ReportQuery(graphene.ObjectType):
    submitted_reports = graphene.List(ReportType)
    report = graphene.Field(ReportType, report_id=graphene.UUID(required=True))
    reports = graphene.List(
        ReportType,
        status=ReportStatusEnum(required=False),
        reason_id=graphene.UUID(required=False),
        user_id=graphene.UUID(required=False),
    )
    report_count = graphene.Int(
        status=ReportStatusEnum(required=False),
        reason_id=graphene.UUID(required=False),
        user_id=graphene.UUID(required=False),
    )
    report_reasons = graphene.List(
        ReportReasonType,
        target_type=ReportTargetTypeEnum(required=False),
    )

    @login_required
    def resolve_submitted_reports(self, info: graphene.ResolveInfo) -> QuerySet[Report]:
        return Report.objects.filter(user=info.context.user).select_related(
            "reason", "moderator", "user", "content_type"
        )

    @login_required
    def resolve_report(
        self, info: graphene.ResolveInfo, report_id: uuid.UUID
    ) -> Report:
        try:
            report = Report.objects.select_related(
                "reason", "moderator", "content_type"
            ).get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError(
                "Report not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        if report.user != info.context.user:
            raise GraphQLError(
                "Permission denied", extensions={"code": ErrorCode.PERMISSION_DENIED}
            )

        return report

    # TODO: Add cursor based pagination
    @superuser_required
    def resolve_reports(
        self,
        info: graphene.ResolveInfo,
        status: Optional[ReportStatus] = None,
        reason_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> QuerySet[Report]:
        queryset = Report.objects.select_related(
            "user", "reason", "moderator", "content_type"
        )

        if status:
            queryset = queryset.filter(status=status)
        if reason_id:
            queryset = queryset.filter(reason_id=reason_id)
        if user_id:
            queryset = queryset.filter(user__id=user_id)

        return queryset

    @superuser_required
    def resolve_report_count(
        self,
        info: graphene.ResolveInfo,
        status: Optional[ReportStatus] = None,
        reason_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> int:
        queryset = Report.objects.all()
        if status:
            queryset = queryset.filter(status=status)
        if reason_id:
            queryset = queryset.filter(reason_id=reason_id)
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        return queryset.count()

    @login_required
    def resolve_report_reasons(
        self,
        info: graphene.ResolveInfo,
        target_type: Optional[ReportTargetTypeEnum] = None,
    ) -> QuerySet[ReportReason]:
        from django.db.models import Count, Q

        queryset = ReportReason.objects.filter(is_active=True)
        if target_type is not None:
            model_map = {
                ReportTargetTypeEnum.ROOM: Room,
                ReportTargetTypeEnum.USER: User,
            }
            model = model_map.get(target_type)
            if model is not None:
                ct = ContentType.objects.get_for_model(model)
                queryset = (
                    queryset.annotate(ct_count=Count("allowed_content_types"))
                    .filter(Q(ct_count=0) | Q(allowed_content_types=ct))
                    .distinct()
                )
        return queryset
