import graphene
from graphene_django import DjangoObjectType

from backend.account.models import UserBanHistory, UserHistory, User
from backend.moderation.models import (
    ModerationActionHistory,
    ModerationCaseHistory,
    ReportHistory,
)
from backend.room.models import RoomHistory
from backend.invite.models import InviteHistory, InviteLinkHistory


class BaseAuditType(graphene.ObjectType):
    actor = graphene.Field("backend.graphql.account.types.UserType")
    pgh_id = graphene.ID()
    pgh_created_at = graphene.DateTime()
    pgh_label = graphene.String()
    pgh_obj_id = graphene.UUID()

    def resolve_actor(self, info):
        if self.pgh_context:
            user_id = self.pgh_context.metadata.get("user")
            if user_id:
                return User.objects.filter(id=user_id).first()
        return None


class UserBanAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = UserBanHistory
        interfaces = (graphene.relay.Node,)
        fields = ("user", "banned_by", "reason", "expires_at", "is_active")


class UserAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = UserHistory
        interfaces = (graphene.relay.Node,)
        fields = (
            "username",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
        )


class RoomAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = RoomHistory
        interfaces = (graphene.relay.Node,)
        fields = (
            "name",
            "description",
            "visibility",
            "default_role",
        )


class InviteAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = InviteHistory
        interfaces = (graphene.relay.Node,)
        fields = (
            "status",
            "role",
        )


class InviteLinkAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = InviteLinkHistory
        interfaces = (graphene.relay.Node,)
        fields = (
            "is_active",
            "role",
            "max_uses",
            "expires_at",
        )


class ModerationCaseAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = ModerationCaseHistory
        interfaces = (graphene.relay.Node,)
        fields = (
            "status",
            "priority",
        )


class ModerationActionAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = ModerationActionHistory
        interfaces = (graphene.relay.Node,)
        fields = ("action", "note", "moderator")


class ReportAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = ReportHistory
        interfaces = (graphene.relay.Node,)
        fields = (
            "description",
            "reason",
            "case",
        )
