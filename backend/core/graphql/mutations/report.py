import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.db import transaction, IntegrityError
from backend.core.graphql.types import ReportType, ReportReasonEnum, ReportStatusEnum
from backend.core.graphql.utils import format_form_errors
from backend.core.models import Participant, Report, Room
from backend.core.forms import ReportForm


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
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})

        if not Participant.objects.filter(user=info.context.user, room=room).exists():
            raise GraphQLError(
                "You must be a participant of the room to report it", 
                extensions={"code": "NOT_PARTICIPANT"}
            )

        if Report.active_reports(user=info.context.user, room=room).exists():
            raise GraphQLError(
                "You already have an active report targeting this room.",
                extensions={"code": "ALREADY_REPORTED"},
            )
        data = {
            "reason": reason,
            "body": body,
        }
        
        form = ReportForm(data=data)
        
        if not form.is_valid():
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})

        with transaction.atomic():
            report = form.save(commit=False)
            report.user = info.context.user
            report.room = room
            
            try:
                report.save()
            except IntegrityError:
                raise GraphQLError(
                    "Could not create report due to a conflict.",
                    extensions={"code": "CONFLICT"},
                )
        
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
        # TODO: (maybe) FORM
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError("Report not found", extensions={"code": "NOT_FOUND"})

        if status is not None:
            report.status = status
        if moderator_note is not None:
            report.moderator_note = moderator_note

        report.moderator = info.context.user
        report.save()

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
            raise GraphQLError("Report not found", extensions={"code": "NOT_FOUND"})

        report.delete()
        return DeleteReport(success=True)


class ReportMutation(graphene.ObjectType):
    create_report = CreateReport.Field()
    update_report = UpdateReport.Field()
    delete_report = DeleteReport.Field()
