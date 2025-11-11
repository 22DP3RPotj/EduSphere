import graphene
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from backend.core.graphql.types import ReportType, ReportReasonEnum, ReportStatusEnum
from backend.core.models import Report, Room


class CreateReport(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        reason = ReportReasonEnum(required=True)
        body = graphene.String(required=True)

    report = graphene.Field(ReportType)

    @login_required
    def mutate(self, info, room_id, reason, body):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})

        if not room.participants.filter(id=info.context.user.id).exists():
            raise GraphQLError(
                "You must be a participant of the room to report it", 
                extensions={"code": "NOT_PARTICIPANT"}
            )

        if Report.objects.filter(user=info.context.user, room=room).exists():
            raise GraphQLError(
                "You have already reported this room",
                extensions={"code": "ALREADY_REPORTED"}
            )

        report = Report(
            user=info.context.user,
            room=room,
            reason=reason,
            body=body
        )
        report.save()

        return CreateReport(report=report)


class UpdateReport(graphene.Mutation):
    class Arguments:
        report_id = graphene.UUID(required=True)
        status = ReportStatusEnum(required=False)
        moderator_note = graphene.String(required=False)

    report = graphene.Field(ReportType)

    @superuser_required
    def mutate(self, info, report_id, **kwargs):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise GraphQLError("Report not found", extensions={"code": "NOT_FOUND"})

        if 'status' in kwargs:
            report.status = kwargs['status']
        if 'moderator_note' in kwargs:
            report.moderator_note = kwargs['moderator_note']
        
        report.moderator = info.context.user
        report.save()

        return UpdateReport(report=report)


class DeleteReport(graphene.Mutation):
    class Arguments:
        report_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @superuser_required
    def mutate(self, info, report_id):
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
