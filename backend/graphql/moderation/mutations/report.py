import graphene
import uuid
from typing import Union
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from backend.core.exceptions import (
    ErrorCode,
    PermissionException,
    ConflictException,
    FormValidationException,
)
from backend.graphql.moderation.types import (
    ActionEnum,
    ModerationCaseType,
    ReportType,
    ReportTargetTypeEnum,
)
from backend.moderation.choices import ActionChoices
from backend.moderation.models import ModerationCase, Report, ReportReason
from backend.room.models import Room
from backend.account.models import User
from backend.moderation.services import ReportService


class CreateReport(graphene.Mutation):
    class Arguments:
        target_type = ReportTargetTypeEnum(required=True)
        target_id = graphene.UUID(required=True)
        reason_id = graphene.UUID(required=True)
        description = graphene.String(required=True)

    report = graphene.Field(ReportType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        target_type: ReportTargetTypeEnum,
        target_id: uuid.UUID,
        reason_id: uuid.UUID,
        description: str,
    ):
        model_map: dict[str, Union[type[Room], type[User]]] = {
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
                reporter=info.context.user,
                target=target,
                reason=reason,
                description=description,
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except ConflictException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})

        return CreateReport(report=report)


class TakeCaseAction(graphene.Mutation):
    class Arguments:
        case_id = graphene.UUID(required=True)
        action = ActionEnum(required=True)
        note = graphene.String(required=False)

    case = graphene.Field(ModerationCaseType)

    @superuser_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        case_id: uuid.UUID,
        action: ActionChoices,
        note: str = "",
    ):
        try:
            case = ModerationCase.objects.get(id=case_id)
        except ModerationCase.DoesNotExist:
            raise GraphQLError(
                "Case not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            case = ReportService.take_case_action(
                moderator=info.context.user,
                case=case,
                action=action,
                note=note,
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return TakeCaseAction(case=case)


class SetCaseUnderReview(graphene.Mutation):
    class Arguments:
        case_id = graphene.UUID(required=True)

    case = graphene.Field(ModerationCaseType)

    @superuser_required
    def mutate(self, info: graphene.ResolveInfo, case_id: uuid.UUID):
        try:
            case = ModerationCase.objects.get(id=case_id)
        except ModerationCase.DoesNotExist:
            raise GraphQLError(
                "Case not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            case = ReportService.set_case_under_review(
                moderator=info.context.user,
                case=case,
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return SetCaseUnderReview(case=case)


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
