import graphene
from graphene_django import DjangoObjectType

from backend.moderation.models import (
    ModerationAction,
    ModerationCase,
    Report,
    ReportHistory,
    ReportReason,
)
from backend.graphql.room.types import RoomType
from backend.graphql.account.types import UserType
from backend.graphql.messaging.types import MessageType


class CaseStatusEnum(graphene.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ActionPriorityEnum(graphene.Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class ActionEnum(graphene.Enum):
    NO_VIOLATION = "NO_VIOLATION"
    CONTENT_REMOVED = "CONTENT_REMOVED"
    WARNING = "WARNING"
    TEMP_BAN = "TEMP_BAN"
    PERM_BAN = "PERM_BAN"


class ReportTargetTypeEnum(graphene.Enum):
    ROOM = "room"
    USER = "user"
    MESSAGE = "message"


class ReportReasonType(DjangoObjectType):
    class Meta:
        model = ReportReason
        fields = ("id", "slug", "label", "is_active")


class ReportTargetType(graphene.Union):
    class Meta:
        types = (RoomType, UserType, MessageType)

    @classmethod
    def resolve_type(cls, instance, info):
        from backend.room.models import Room
        from backend.account.models import User
        from backend.messaging.models import Message

        if isinstance(instance, Room):
            return RoomType
        if isinstance(instance, User):
            return UserType
        if isinstance(instance, Message):
            return MessageType
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

    def resolve_action(self, info: graphene.ResolveInfo):
        return str(self.action)


class ModerationCaseType(DjangoObjectType):
    status = graphene.Field(CaseStatusEnum, required=True)
    priority = graphene.Int(required=True)
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

    def resolve_status(self, info: graphene.ResolveInfo):
        return str(self.status)

    def resolve_priority(self, info: graphene.ResolveInfo):
        return int(self.priority)

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
