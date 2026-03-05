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
from backend.graphql.moderation.types import (
    ReportType,
    ReportStatusEnum,
    ReportTargetTypeEnum,
)
from backend.moderation.choices import ReportStatus
from backend.moderation.models import Report, ReportReason
from backend.room.models import Room
from backend.account.models import User
from backend.moderation.services import ReportService


class CreateReport(graphene.Mutation):
    class Arguments:
        target_type = ReportTargetTypeEnum(required=True)
        target_id = graphene.UUID(required=True)
        reason_id = graphene.UUID(required=True)
        body = graphene.String(required=True)

    report = graphene.Field(ReportType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        target_type: ReportTargetTypeEnum,
        target_id: uuid.UUID,
        reason_id: uuid.UUID,
        body: str,
    ):
        model_map = {
            ReportTargetTypeEnum.ROOM: Room,
            ReportTargetTypeEnum.USER: User,
        }
        TargetModel = model_map[target_type]

        try:
            target = TargetModel.objects.get(id=target_id)
        except TargetModel.DoesNotExist:
            raise GraphQLError(
                "Target not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            reason = ReportReason.objects.get(id=reason_id)
        except ReportReason.DoesNotExist:
            raise GraphQLError(
                "Report reason not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            report = ReportService.create_report(
                reporter=info.context.user, target=target, reason=reason, body=body
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
        status: Optional[ReportStatus] = None,
        moderator_note: Optional[str] = None,
    ):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError(
                "Report not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            report = ReportService.update_report_status(
                moderator=info.context.user,
                report=report,
                new_status=status
                if status is not None
                else ReportStatus(report.status),
                moderator_note=moderator_note,
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
            raise GraphQLError(
                "Report not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        report.delete()
        return DeleteReport(success=True)
