import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet, Count, Q

from backend.account.models import User
from backend.core.exceptions import ErrorCode
from backend.graphql.moderation.filters import ReportFilter, ModerationCaseFilter
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
from backend.messaging.models import Message


class ReportQuery(graphene.ObjectType):
    submitted_reports = graphene.List(ReportType)
    report = graphene.Field(ReportType, report_id=graphene.UUID(required=True))
    reports = graphene.List(
        ReportType,
        reason=graphene.UUID(),
        reporter=graphene.UUID(),
        case=graphene.UUID(),
        has_case=graphene.Boolean(),
        target_type=ReportTargetTypeEnum(),
        created_after=graphene.DateTime(),
        created_before=graphene.DateTime(),
    )
    report_count = graphene.Int(
        reason=graphene.UUID(),
        reporter=graphene.UUID(),
        case=graphene.UUID(),
        has_case=graphene.Boolean(),
        target_type=ReportTargetTypeEnum(),
        created_after=graphene.DateTime(),
        created_before=graphene.DateTime(),
    )
    report_reasons = graphene.List(
        ReportReasonType,
        target_type=ReportTargetTypeEnum(required=False),
    )
    cases = graphene.List(
        ModerationCaseType,
        status=CaseStatusEnum(),
        priority=graphene.Int(),
        has_actions=graphene.Boolean(),
        target_type=ReportTargetTypeEnum(),
        created_after=graphene.DateTime(),
        created_before=graphene.DateTime(),
        updated_after=graphene.DateTime(),
        updated_before=graphene.DateTime(),
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
        reason: Optional[uuid.UUID] = None,
        reporter: Optional[uuid.UUID] = None,
        case: Optional[uuid.UUID] = None,
        has_case: Optional[bool] = None,
        target_type: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
    ) -> QuerySet[Report]:
        queryset = Report.objects.select_related(
            "reporter", "reason", "content_type", "case"
        )
        filter_data = {
            k: v
            for k, v in {
                "reason": reason,
                "reporter": reporter,
                "case": case,
                "has_case": has_case,
                "target_type": target_type,
                "created_after": created_after,
                "created_before": created_before,
            }.items()
            if v is not None
        }
        return ReportFilter(filter_data, queryset=queryset).qs

    @superuser_required
    def resolve_report_count(
        self,
        info: graphene.ResolveInfo,
        reason: Optional[uuid.UUID] = None,
        reporter: Optional[uuid.UUID] = None,
        case: Optional[uuid.UUID] = None,
        has_case: Optional[bool] = None,
        target_type: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
    ) -> int:
        return self.resolve_reports(
            info,
            reason=reason,
            reporter=reporter,
            case=case,
            has_case=has_case,
            target_type=target_type,
            created_after=created_after,
            created_before=created_before,
        ).count()

    @login_required
    def resolve_report_reasons(
        self,
        info: graphene.ResolveInfo,
        target_type: Optional[ReportTargetTypeEnum] = None,
    ) -> QuerySet[ReportReason]:
        queryset = ReportReason.objects.filter(is_active=True)
        if target_type is not None:
            model_map = {
                ReportTargetTypeEnum.ROOM: Room,
                ReportTargetTypeEnum.USER: User,
                ReportTargetTypeEnum.MESSAGE: Message,
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

    # TODO: Add cursor based pagination
    @superuser_required
    def resolve_cases(
        self,
        info: graphene.ResolveInfo,
        status: Optional[CaseStatusChoices] = None,
        priority: Optional[int] = None,
        has_actions: Optional[bool] = None,
        target_type: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        updated_after: Optional[str] = None,
        updated_before: Optional[str] = None,
    ) -> QuerySet[ModerationCase]:
        queryset = ModerationCase.objects.prefetch_related("reports", "actions")
        filter_data = {
            k: v
            for k, v in {
                "status": status,
                "priority": priority,
                "has_actions": has_actions,
                "target_type": target_type,
                "created_after": created_after,
                "created_before": created_before,
                "updated_after": updated_after,
                "updated_before": updated_before,
            }.items()
            if v is not None
        }
        return ModerationCaseFilter(filter_data, queryset=queryset).qs

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
