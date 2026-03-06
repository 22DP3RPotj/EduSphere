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
    CaseStatusEnum,
    ModerationCaseType,
    ReportTargetTypeEnum,
)
from backend.moderation.choices import CaseStatusChoices
from backend.moderation.models import ModerationCase, Report, ReportReason
from backend.room.models import Room


class ReportQuery(graphene.ObjectType):
    submitted_reports = graphene.List(ReportType)
    report = graphene.Field(ReportType, report_id=graphene.UUID(required=True))
    reports = graphene.List(
        ReportType,
        reason_id=graphene.UUID(required=False),
        reporter_id=graphene.UUID(required=False),
    )
    report_count = graphene.Int(
        reason_id=graphene.UUID(required=False),
        reporter_id=graphene.UUID(required=False),
    )
    report_reasons = graphene.List(
        ReportReasonType,
        target_type=ReportTargetTypeEnum(required=False),
    )
    cases = graphene.List(
        ModerationCaseType,
        status=CaseStatusEnum(required=False),
    )
    case = graphene.Field(ModerationCaseType, case_id=graphene.UUID(required=True))

    @login_required
    def resolve_submitted_reports(self, info: graphene.ResolveInfo) -> QuerySet[Report]:
        return Report.objects.filter(reporter=info.context.user).select_related(
            "reason", "reporter", "content_type", "case"
        )

    @login_required
    def resolve_report(
        self, info: graphene.ResolveInfo, report_id: uuid.UUID
    ) -> Report:
        try:
            report = Report.objects.select_related(
                "reporter", "reason", "content_type", "case"
            ).get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError(
                "Report not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        if report.reporter != info.context.user:
            raise GraphQLError(
                "Permission denied", extensions={"code": ErrorCode.PERMISSION_DENIED}
            )

        return report

    # TODO: Add cursor based pagination
    @superuser_required
    def resolve_reports(
        self,
        info: graphene.ResolveInfo,
        reason_id: Optional[uuid.UUID] = None,
        reporter_id: Optional[uuid.UUID] = None,
    ) -> QuerySet[Report]:
        queryset = Report.objects.select_related(
            "reporter", "reason", "content_type", "case"
        )

        if reason_id:
            queryset = queryset.filter(reason_id=reason_id)
        if reporter_id:
            queryset = queryset.filter(reporter_id=reporter_id)

        return queryset

    @superuser_required
    def resolve_report_count(
        self,
        info: graphene.ResolveInfo,
        reason_id: Optional[uuid.UUID] = None,
        reporter_id: Optional[uuid.UUID] = None,
    ) -> int:
        queryset = Report.objects.all()
        if reason_id:
            queryset = queryset.filter(reason_id=reason_id)
        if reporter_id:
            queryset = queryset.filter(reporter_id=reporter_id)
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

    @superuser_required
    def resolve_cases(
        self,
        info: graphene.ResolveInfo,
        status: Optional[CaseStatusChoices] = None,
    ) -> QuerySet[ModerationCase]:
        queryset = ModerationCase.objects.prefetch_related("reports", "actions")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @superuser_required
    def resolve_case(
        self, info: graphene.ResolveInfo, case_id: uuid.UUID
    ) -> ModerationCase:
        try:
            return ModerationCase.objects.prefetch_related("reports", "actions").get(
                id=case_id
            )
        except ModerationCase.DoesNotExist:
            raise GraphQLError(
                "Case not found", extensions={"code": ErrorCode.NOT_FOUND}
            )
