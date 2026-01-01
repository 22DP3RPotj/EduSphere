import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from backend.core.exceptions import (
    ErrorCode,
    PermissionException,
    ConflictException,
    FormValidationException,
)
from backend.graphql.moderation.types import ReportType, ReportReasonEnum, ReportStatusEnum
from backend.moderation.models import Report
from backend.room.models import Room
from backend.moderation.services import ReportService


class CreateReport(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        reason = ReportReasonEnum(required=True)
        body = graphene.String(required=True)

    report = graphene.Field(ReportType)
    
    @login_required
    def mutate(self, info: graphene.ResolveInfo, room_id: uuid.UUID, reason: Report.ReportReason, body: str):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": ErrorCode.NOT_FOUND})

        try:
            report = ReportService.create_report(
                reporter=info.context.user,
                room=room,
                reason=reason,
                body=body
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except ConflictException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})
        
        return CreateReport(report=report)


class UpdateReport(graphene.Mutation):
    class Arguments:
        report_id = graphene.UUID(required=True)
        status = ReportStatusEnum(required=False)
        moderator_note = graphene.String(required=False)

    report = graphene.Field(ReportType)

    @superuser_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        report_id: uuid.UUID,
        status: Optional[Report.ReportStatus] = None,
        moderator_note: Optional[str] = None
    ):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError("Report not found", extensions={"code": ErrorCode.NOT_FOUND})

        try:
            report = ReportService.update_report_status(
                moderator=info.context.user,
                report=report,
                new_status=status if status is not None else report.status,
                moderator_note=moderator_note
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return UpdateReport(report=report)


class DeleteReport(graphene.Mutation):
    class Arguments:
        report_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @superuser_required
    def mutate(self, info: graphene.ResolveInfo, report_id: uuid.UUID):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError("Report not found", extensions={"code": ErrorCode.NOT_FOUND})

        report.delete()
        return DeleteReport(success=True)
