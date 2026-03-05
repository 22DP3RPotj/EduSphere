import graphene
from graphene_django import DjangoObjectType

from backend.core.models import CoreEvent
from backend.moderation.models import Report, ReportHistory, ReportReason
from backend.graphql.room.types import RoomType
from backend.graphql.account.types import UserType


ReportStatusEnum = graphene.Enum.from_enum(Report.Status)


class ReportTargetTypeEnum(graphene.Enum):
    ROOM = "room"
    USER = "user"


class ReportReasonType(DjangoObjectType):
    class Meta:
        model = ReportReason
        fields = ("id", "slug", "label", "is_active")


class ReportTargetType(graphene.Union):
    class Meta:
        types = (RoomType, UserType)

    @classmethod
    def resolve_type(cls, instance, info):
        from backend.room.models import Room
        from backend.account.models import User

        if isinstance(instance, Room):
            return RoomType
        if isinstance(instance, User):
            return UserType
        return None


class ReportType(DjangoObjectType):
    reason = graphene.Field(ReportReasonType, required=True)
    status = graphene.Field(ReportStatusEnum, required=True)
    target = graphene.Field(ReportTargetType)

    user = graphene.Field("backend.graphql.account.types.UserType", required=True)
    moderator = graphene.Field("backend.graphql.account.types.UserType")

    class Meta:
        model = Report
        fields = (
            "id",
            "user",
            "body",
            "reason",
            "status",
            "moderator_note",
            "moderator",
            "created_at",
            "updated_at",
        )

    def resolve_target(self, info: graphene.ResolveInfo):
        return self.content_object


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
