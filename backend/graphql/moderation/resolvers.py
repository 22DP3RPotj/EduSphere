import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.db.models import QuerySet

from backend.core.exceptions import ErrorCode
from backend.graphql.moderation.types import ReportType, ReportReasonEnum, ReportStatusEnum
from backend.moderation.models import Report


class ReportQuery(graphene.ObjectType):
    submitted_reports = graphene.List(ReportType)
    report = graphene.Field(
        ReportType,
        report_id=graphene.UUID(required=True)
    )
    reports = graphene.List(
        ReportType,
        status=ReportStatusEnum(required=False),
        reason=ReportReasonEnum(required=False),
        user_id=graphene.UUID(required=False),
    )
    report_count = graphene.Int(
        status=ReportStatusEnum(required=False),
        reason=ReportReasonEnum(required=False),
        user_id=graphene.UUID(required=False),
    )

    @login_required
    def resolve_submitted_reports(self, info: graphene.ResolveInfo) -> QuerySet[Report]:
        return Report.objects.filter(user=info.context.user).select_related('room', 'moderator', 'user')

    @login_required
    def resolve_report(self, info: graphene.ResolveInfo, report_id: uuid.UUID) -> Report:
        try:
            report = Report.objects.select_related('room', 'moderator').get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError("Report not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        if report.user != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": ErrorCode.PERMISSION_DENIED})
        
        return report

    # TODO: Add pagination
    @superuser_required
    def resolve_reports(
        self,
        info: graphene.ResolveInfo,
        status: Optional[Report.ReportStatus] = None,
        reason: Optional[Report.ReportReason] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> QuerySet[Report]:
        queryset = Report.objects.select_related('user', 'room', 'moderator')
        
        if status:
            queryset = queryset.filter(status=status)
        if reason:
            queryset = queryset.filter(reason=reason)
        if user_id:
            queryset = queryset.filter(user__id=user_id)
            
        return queryset
    
    @superuser_required
    def resolve_report_count(
        self,
        info: graphene.ResolveInfo,
        status: Optional[Report.ReportStatus] = None,
        reason: Optional[Report.ReportReason] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> int:
        return self.filter(status=status, reason=reason, user_id=user_id).count()
