import graphene
from graphene_django import DjangoObjectType

from backend.moderation.models import Report


ReportReasonEnum = graphene.Enum.from_enum(Report.ReportReason)
ReportStatusEnum = graphene.Enum.from_enum(Report.ReportStatus)


class ReportType(DjangoObjectType):
    reason = graphene.Field(ReportReasonEnum, required=True)
    status = graphene.Field(ReportStatusEnum, required=True)

    user = graphene.Field("backend.graphql.types.UserType")
    moderator = graphene.Field("backend.graphql.types.UserType")

    class Meta:
        model = Report
        fields = (
            "id",
            "user",
            "room",
            "body",
            "reason",
            "status",
            "moderator_note",
            "moderator",
            "created_at",
            "updated_at",
        )
