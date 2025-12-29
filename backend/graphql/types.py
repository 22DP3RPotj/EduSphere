import graphene
from graphene_django.types import DjangoObjectType

from backend.core.models import User, Room, Topic, Message, Report, Participant, Role, Permission, Invite


ReportReasonEnum = graphene.Enum.from_enum(Report.ReportReason)
ReportStatusEnum = graphene.Enum.from_enum(Report.ReportStatus)
RoomVisibilityEnum = graphene.Enum.from_enum(Room.Visibility)
InviteStatusEnum = graphene.Enum.from_enum(Invite.InviteStatus)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "bio",
            "avatar",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
        )


class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = (
            "id",
            "name",
        )


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = (
            "id",
            "code",
            "description"
        )
        

class RoleType(DjangoObjectType):
    permissions = graphene.List(PermissionType)
    
    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "permissions",
        )


class ParticipantType(DjangoObjectType):
    id = graphene.UUID(required=True)
    user = graphene.Field(UserType, required=True)
    role = graphene.Field(RoleType)
    username = graphene.String()
    avatar = graphene.String()

    class Meta:
        model = Participant
        fields = (
            "id",
            "user",
            "role",
            "joined_at",
        )

    def resolve_id(self, info):
        return self.user.id
    
    def resolve_username(self, info):
        return self.user.username
    
    def resolve_avatar(self, info):
        return self.user.avatar

# TODO: Return UserType instead of ParticipantType
class RoomType(DjangoObjectType):
    participants = graphene.List(ParticipantType)
    topics = graphene.List(TopicType)
    host = graphene.Field(UserType, required=True)
    visibility = graphene.Field(RoomVisibilityEnum, required=True)

    class Meta:
        model = Room
        fields = (
            "id",
            "host",
            "topics",
            "name",
            "slug",
            "visibility",
            "description",
            "participants",
            "updated_at",
            "created_at",
        )
    
    def resolve_participants(self, info):
        return Participant.objects.select_related("user", "role").filter(room=self)
    
    def resolve_topics(self, info):
        return self.topics.all()
    
    
class MessageType(DjangoObjectType):
    user = graphene.Field(UserType, required=True)
    room = graphene.Field(RoomType)
    
    class Meta:
        model = Message
        fields = (
            "id",
            "user",
            "room",
            "body",
            "is_edited",
            "created_at",
            "updated_at",
        )


class ReportType(DjangoObjectType):
    reason = graphene.Field(ReportReasonEnum, required=True)
    status = graphene.Field(ReportStatusEnum, required=True)

    user = graphene.Field(UserType)
    moderator = graphene.Field(UserType)

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


class InviteType(DjangoObjectType):
    inviter = graphene.Field(UserType, required=True)
    invitee = graphene.Field(UserType, required=True)
    role = graphene.Field(RoleType, required=True)
    
    class Meta:
        model = Invite
        fields = (
            "id",
            "inviter",
            "invitee",
            "role",
            "token",
            "status",
            "created_at",
            "expires_at",
        )


class AuthStatusType(graphene.ObjectType):
    is_authenticated = graphene.Boolean(required=True)
    user = graphene.Field(UserType)
