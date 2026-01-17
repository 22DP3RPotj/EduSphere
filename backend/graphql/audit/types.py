import graphene
from graphene_django import DjangoObjectType

from backend.account.models import UserHistory, User
from backend.room.models import RoomHistory
from backend.invite.models import InviteHistory


class BaseAuditType(graphene.ObjectType):
    actor = graphene.Field("backend.graphql.account.types.UserType")
    pgh_id = graphene.ID()
    pgh_created_at = graphene.DateTime()
    pgh_label = graphene.String()
    pgh_obj_id = graphene.UUID()

    def resolve_actor(self, info):
        context = self.pgh_context or {}
        user_id = context.get("user")
        if user_id:
            return User.objects.filter(id=user_id).first()
        return None


class UserAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = UserHistory
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
        fields = (
            "name",
            "description",
            "visibility",
            "default_role",
        )


class InviteAuditType(BaseAuditType, DjangoObjectType):
    class Meta:
        model = InviteHistory
        fields = (
            "status",
            "role",
        )
