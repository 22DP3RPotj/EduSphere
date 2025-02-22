import graphene
import graphql_jwt
from .types import UserType, RoomType
from .models import Room, Topic, Message
from .forms import UserForm, RegisterForm, RoomForm
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token
from graphql import GraphQLError


class RegisterUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    user = graphene.Field(UserType)
    token = graphene.String()

    def mutate(self, info, **kwargs):
        form = RegisterForm(kwargs)
        
        if form.is_valid():
            user = form.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(info.context, user, backend=user.backend)
            token = get_token(user)
            return RegisterUser(user=user, token=token)
        else:
            raise GraphQLError(form.errors.as_json())
    

class UpdateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=False)
        name = graphene.String(required=False)
        email = graphene.String(required=False)
        bio = graphene.String(required=False)
        avatar = Upload(required=False)  # File upload support

    user = graphene.Field(UserType)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        avatar = kwargs.pop("avatar", None)  # Extract file separately
        
        form = UserForm(
            data=kwargs,
            files={"avatar": avatar} if avatar else None,
            instance=user
        )

        if form.is_valid():
            form.save()
            return UpdateUser(user=user)
        else:
            raise GraphQLError(form.errors.as_json())

class CreateRoom(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        topic_name = graphene.String(required=True)
        description = graphene.String()

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info, name, topic_name, description=None):
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
            return CreateRoom(room=room)
        else:
            raise GraphQLError(form.errors.as_json())


class DeleteRoom(graphene.Mutation):
    class Arguments:
        host_username = graphene.String(required=True)
        room_slug = graphene.String(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, host_username, room_slug):
        room = get_object_or_404(
            Room,
            host__username=host_username,
            slug=room_slug
        )
        
        if room.host != info.context.user:
            raise PermissionError("Not room host")
            
        room.delete()
        return DeleteRoom(success=True)

class DeleteMessage(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, message_id):
        message = Message.objects.get(id=message_id)
        if message.user != info.context.user:
            raise GraphQLError("Not message author")
        message.delete()
        return DeleteMessage(success=True)
    
    

class JoinRoom(graphene.Mutation):
    class Arguments:
        host_slug = graphene.String(required=True)
        room_slug = graphene.String(required=True)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info, host_slug, room_slug):
        room = get_object_or_404(
            Room,
            host__slug=host_slug,
            slug=room_slug
        )
        room.participants.add(info.context.user)
        return JoinRoom(room=room)
    

class AppMutation(graphene.ObjectType):
    update_user = UpdateUser.Field()
    create_room = CreateRoom.Field()
    join_room = JoinRoom.Field()
    register_user = RegisterUser.Field()
    delete_room = DeleteRoom.Field()
    delete_message = DeleteMessage.Field()

class AuthMutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

class Mutation(AppMutation, AuthMutation, graphene.ObjectType):
    pass
