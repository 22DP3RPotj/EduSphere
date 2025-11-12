import graphene
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from backend.core.graphql.types import ReportType
from backend.core.models import Report, Room


class ReportQuery(graphene.ObjectType):
    my_reports = graphene.List(ReportType)
    report = graphene.Field(
        ReportType,
        report_id=graphene.UUID(required=True)
    )
    all_reports = graphene.List(
        ReportType,
        status=graphene.String(),
        reason=graphene.String()
    )
    report_count = graphene.Int(
        status=graphene.String(),
        reason=graphene.String()
    )

    @login_required
    def resolve_my_reports(self, info):
        return Report.objects.filter(user=info.context.user).select_related('room', 'moderator', 'user')

    @login_required
    def resolve_report(self, info, report_id):
        try:
            report = Report.objects.select_related('room', 'moderator').get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError("Report not found", extensions={"code": "NOT_FOUND"})
        
        if report.user != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        return report

    # TODO: Add pagination
    @superuser_required
    def resolve_all_reports(self, info, status=None, reason=None, user=None):
        queryset = Report.objects.select_related('user', 'room', 'moderator')
        
        if status:
            queryset = queryset.filter(status=status)
        if reason:
            queryset = queryset.filter(reason=reason)
        if user:
            queryset = queryset.filter(user__username=user)
            
        return queryset
    
    @superuser_required
    def resolve_report_count(self, info, status=None, reason=None, user=None):
        queryset = Report.objects.all()
        
        if status:
            queryset = queryset.filter(status=status)
        if reason:
            queryset = queryset.filter(reason=reason)
        if user:
            queryset = queryset.filter(user__username=user)
        
        return queryset.count()
