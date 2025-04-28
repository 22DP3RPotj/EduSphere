import graphene
from graphene_django.types import DjangoObjectType
from ..models import User, Room, Topic, Message


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "slug", "username", "name", "email", "bio", "avatar")

class RoomType(DjangoObjectType):
    class Meta:
        model = Room
        fields = ("id", "name", "slug", "host", "topic", "description", "participants", "updated", "created")

class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = ("id", "name")

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = ("id", "user", "room", "body", "created", "updated")


class AuthStatusType(graphene.ObjectType):
    is_authenticated = graphene.Boolean(required=True)
    user = graphene.Field(UserType)