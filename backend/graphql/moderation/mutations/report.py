import graphene
import uuid
from typing import Any, Optional, Self, Union
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from backend.core.exceptions import (
    ErrorCode,
)
from backend.graphql.base import BaseMutation
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
from backend.messaging.models import Message
from backend.moderation.services import ReportService


class CreateReport(BaseMutation):
    class Arguments:
        target_type = ReportTargetTypeEnum(required=True)
        target_id = graphene.UUID(required=True)
        reason_id = graphene.UUID(required=True)
        description = graphene.String(required=True)

    report = graphene.Field(ReportType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        target_type: ReportTargetTypeEnum,
        target_id: uuid.UUID,
        reason_id: uuid.UUID,
        description: str,
    ) -> Self:
        model_map: dict[str, Union[type[Room], type[User], type[Message]]] = {
            ReportTargetTypeEnum.ROOM: Room,
            ReportTargetTypeEnum.USER: User,
            ReportTargetTypeEnum.MESSAGE: Message,
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

        report = ReportService.create_report(
            reporter=info.context.user,
            target=target,
            reason=reason,
            description=description,
        )

        return cls(report=report)


class TakeCaseAction(BaseMutation):
    class Arguments:
        case_id = graphene.UUID(required=True)
        action = ActionEnum(required=True)
        note = graphene.String(required=False)

    case = graphene.Field(ModerationCaseType)

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        case_id: uuid.UUID,
        action: ActionChoices,
        note: Optional[str] = None,
    ) -> Self:
        try:
            case = ModerationCase.objects.get(id=case_id)
        except ModerationCase.DoesNotExist:
            raise GraphQLError(
                "Case not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        case = ReportService.take_case_action(
            moderator=info.context.user,
            case=case,
            action=action,
            note=note,
        )

        return cls(case=case)


class SetCaseUnderReview(BaseMutation):
    class Arguments:
        case_id = graphene.UUID(required=True)

    case = graphene.Field(ModerationCaseType)

    @classmethod
    @superuser_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, case_id: uuid.UUID
    ):
        try:
            case = ModerationCase.objects.get(id=case_id)
        except ModerationCase.DoesNotExist:
            raise GraphQLError(
                "Case not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        case = ReportService.set_case_under_review(
            moderator=info.context.user,
            case=case,
        )

        return cls(case=case)


class DeleteReport(BaseMutation):
    class Arguments:
        report_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @classmethod
    @superuser_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, report_id: uuid.UUID
    ):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError(
                "Report not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        report.delete()
        return cls(success=True)
