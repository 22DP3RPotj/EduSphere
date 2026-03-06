import graphene
from graphene_django import DjangoObjectType

from backend.moderation.choices import ActionChoices, CaseStatusChoices
from backend.moderation.models import (
    ModerationAction,
    ModerationCase,
    Report,
    ReportHistory,
    ReportReason,
)
from backend.graphql.room.types import RoomType
from backend.graphql.account.types import UserType


CaseStatusEnum = graphene.Enum.from_enum(CaseStatusChoices)
ActionEnum = graphene.Enum.from_enum(ActionChoices)


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
    reporter = graphene.Field("backend.graphql.account.types.UserType")
    target = graphene.Field(ReportTargetType)

    class Meta:
        model = Report
        fields = (
            "id",
            "reporter",
            "description",
            "reason",
            "case",
            "created_at",
        )

    def resolve_target(self, info: graphene.ResolveInfo):
        return self.content_object


class ModerationActionType(DjangoObjectType):
    action = graphene.Field(ActionEnum, required=True)
    moderator = graphene.Field("backend.graphql.account.types.UserType")

    class Meta:
        model = ModerationAction
        fields = ("id", "action", "note", "moderator", "created_at")


class ModerationCaseType(DjangoObjectType):
    status = graphene.Field(CaseStatusEnum, required=True)
    target = graphene.Field(ReportTargetType)

    class Meta:
        model = ModerationCase
        fields = (
            "id",
            "status",
            "priority",
            "created_at",
            "updated_at",
            "reports",
            "actions",
        )

    def resolve_target(self, info: graphene.ResolveInfo):
        return self.content_object


class ReportHistoryType(DjangoObjectType):
    actor_id = graphene.UUID()

    class Meta:
        model = ReportHistory
        fields = (
            "actor_id",
            "description",
            "reason",
            "case",
        )

    def resolve_actor_id(self, info: graphene.ResolveInfo):
        return self.pgh_context.metadata.get("user", None)
