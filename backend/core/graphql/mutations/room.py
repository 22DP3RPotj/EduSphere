import graphene
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.core.graphql.types import RoomType
from backend.core.graphql.utils import format_form_errors

from backend.core.models import Room, Topic
from backend.core.forms import RoomForm


class CreateRoom(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        topic_names = graphene.List(graphene.String, required=True)
        description = graphene.String(required=True)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info, name, topic_names, description):
        topics = []
        for topic_name in topic_names:
            topic, created = Topic.objects.get_or_create(name=topic_name)
            topics.append(topic)
        
        form = RoomForm({
            "name": name,
            "description": description
        })
        
        if form.is_valid():
            room = form.save(commit=False)
            room.host = info.context.user
            room.save()
            room.topics.set(topics)
            room.participants.add(info.context.user)
            return CreateRoom(room=room)
        else:
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})


class UpdateRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        topic_names = graphene.List(graphene.String, required=False)
        description = graphene.String(required=False)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info, room_id, **kwargs):
        try:
            room = Room.objects.get(
                id=room_id,
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        if room.host != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        if 'topic_names' in kwargs:
            topics = []
            for topic_name in kwargs['topic_names']:
                topic, created = Topic.objects.get_or_create(name=topic_name)
                topics.append(topic)
        else:
            topics = room.topics.all()
        
        form = RoomForm({
            "name": room.name,
            "description": kwargs.get("description", room.description)
        }, instance=room)

        if form.is_valid():
            room = form.save()
            room.topics.set(topics)
            return UpdateRoom(room=room)
        else:
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})
    

class DeleteRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, room_id):
        try:
            room = Room.objects.get(
                id=room_id,
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        if room.host != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
            
        room.delete()
        return DeleteRoom(success=True)


class JoinRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info, room_id):
        try:
            room = Room.objects.get(
                id=room_id,
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        if room.participants.filter(id=info.context.user.id).exists():
            raise GraphQLError(
                "Already a participant of this room",
                extensions={"code": "ALREADY_JOINED"}
            )

        room.participants.add(info.context.user)
        return JoinRoom(room=room)


class RoomMutation(graphene.ObjectType):
    create_room = CreateRoom.Field()
    delete_room = DeleteRoom.Field()
    update_room = UpdateRoom.Field()
    join_room = JoinRoom.Field()
