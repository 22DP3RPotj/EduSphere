import graphene
from graphene_django.types import DjangoObjectType
from ..models import User, Room, Topic, Message, Report


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "name", "bio", "avatar")

class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = ("id", "name")
        
class RoomType(DjangoObjectType):
    topics = graphene.List(TopicType)
    
    class Meta:
        model = Room
        fields = ("id", "name", "slug", "host", "topics", "description", "participants", "updated", "created")
        
    def resolve_topics(self, info):
        return self.topics.all()

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = ("id", "user", "room", "body", "edited", "created", "updated")

class ReportType(DjangoObjectType):
    class Meta:
        model = Report
        fields = ("id", "user", "room", "body", "reason", "status", "moderator_note", "moderator", "created", "updated")

class ReportReasonEnum(graphene.Enum):
    SPAM = 'SPAM'
    HARASSMENT = 'HARASSMENT'
    INAPPROPRIATE_CONTENT = 'INAPPROPRIATE_CONTENT'
    HATE_SPEECH = 'HATE_SPEECH'
    OTHER = 'OTHER'


class ReportStatusEnum(graphene.Enum):
    PENDING = 'PENDING'
    UNDER_REVIEW = 'UNDER_REVIEW'
    RESOLVED = 'RESOLVED'
    DISMISSED = 'DISMISSED'


class AuthStatusType(graphene.ObjectType):
    is_authenticated = graphene.Boolean(required=True)
    user = graphene.Field(UserType)