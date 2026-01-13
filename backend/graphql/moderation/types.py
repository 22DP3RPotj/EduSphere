import graphene
from graphene_django import DjangoObjectType

from backend.core.models import CoreEvent
from backend.moderation.models import ReportHistory
from backend.moderation.models import Report


ReportReasonEnum = graphene.Enum.from_enum(Report.Reason)
ReportStatusEnum = graphene.Enum.from_enum(Report.Status)


class ReportType(DjangoObjectType):
    reason = graphene.Field(ReportReasonEnum, required=True)
    status = graphene.Field(ReportStatusEnum, required=True)

    user = graphene.Field("backend.graphql.account.types.UserType", required=True)
    moderator = graphene.Field("backend.graphql.account.types.UserType")

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


class ReportHistoryType(DjangoObjectType):
    actor_id = graphene.UUID()

    class Meta:
        model = ReportHistory
        fields = (
            "actor_id",
            "body",
            "reason",
            "status",
            "moderator_note",
            "moderator",
        )

    def resolve_actor_id(self, info: graphene.ResolveInfo):
        return self.pgh_context.metadata.get("user", None)


class CoreEventType(DjangoObjectType):
    class Meta:
        model = CoreEvent
        fields = (
            "user",
            "url",
            "remote_addr",
        )
