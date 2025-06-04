import graphene
import graphql_jwt
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from .types import UserType, RoomType, MessageType
from .utils import format_form_errors

from ..models import Room, Topic, Message
from ..forms import UserForm, RegisterForm, RoomForm



class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user, success=True)

class RegisterUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        form = RegisterForm(kwargs)

        if form.is_valid():
            user = form.save()
            return RegisterUser(user=user, success=True)
        else:
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})
     
class UpdateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=False)
        bio = graphene.String(required=False)
        avatar = Upload(required=False)

    user = graphene.Field(UserType)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        
        data = {
            "username": user.username,
            "name": kwargs.get("name", user.name),
            "bio": kwargs.get("bio", user.bio),
        }
        
        avatar = kwargs.pop("avatar", None)
        
        form = UserForm(
            data=data,
            files={"avatar": avatar} if avatar else None,
            instance=user
        )

        if form.is_valid():
            form.save()
            return UpdateUser(user=user)
        else:
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})


class CreateRoom(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        topic_name = graphene.String(required=True)
        description = graphene.String(required=True)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info, name, topic_name, description):
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        form = RoomForm({
            "name": name,
            "topic": topic.id,
            "description": description
        })
        
        if form.is_valid():
            room = form.save(commit=False)
            room.host = info.context.user
            room.save()
            room.participants.add(info.context.user)
            return CreateRoom(room=room)
        else:
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})

class UpdateRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        topic_name = graphene.String(required=False)
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
        
        topic, created = Topic.objects.get_or_create(name=kwargs.get("topic_name"))
        
        form = RoomForm({
            "name": room.name,
            "topic": topic.id,
            "description": kwargs.get("description", room.description)
        }, instance=room)

        if form.is_valid():
            form.save()
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

        room.participants.add(info.context.user)
        return JoinRoom(room=room)

class DeleteMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError("Message not found", extensions={"code": "NOT_FOUND"})
        
        if message.user != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        message.delete()
        return DeleteMessage(success=True)
    
    
class UpdateMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)
        body = graphene.String(required=True)

    message = graphene.Field(MessageType)

    @login_required
    def mutate(self, info, message_id, body):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise GraphQLError("Message not found", extensions={"code": "NOT_FOUND"})
        
        if message.user != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        message.update(body)
        return UpdateMessage(message=message)
    

class AppMutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    update_user = UpdateUser.Field()
    create_room = CreateRoom.Field()
    delete_room = DeleteRoom.Field()
    update_room = UpdateRoom.Field()
    join_room = JoinRoom.Field()
    delete_message = DeleteMessage.Field()
    update_message = UpdateMessage.Field()

class AuthMutation(graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    delete_token  = graphql_jwt.DeleteJSONWebTokenCookie.Field()
    delete_refresh_token = graphql_jwt.DeleteRefreshTokenCookie.Field()

class Mutation(AppMutation, AuthMutation, graphene.ObjectType):
    pass
