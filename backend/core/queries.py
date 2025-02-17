import graphene
from .types import RoomType, TopicType, MessageType, UserType
from .models import Room, Topic, Message
from graphql_jwt.decorators import login_required

class Query(graphene.ObjectType):
    all_rooms = graphene.List(RoomType)
    all_topics = graphene.List(TopicType)
    all_messages = graphene.List(MessageType, room_id=graphene.UUID(required=True))

    me = graphene.Field(UserType)  # Get authenticated user

    @login_required
    def resolve_me(self, info):
        return info.context.user

    def resolve_all_rooms(self, info):
        return Room.objects.all()

    def resolve_all_topics(self, info):
        return Topic.objects.all()

    def resolve_all_messages(self, info, room_id):
        return Message.objects.filter(room__id=room_id)
