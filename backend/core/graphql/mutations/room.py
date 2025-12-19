import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from django.db import IntegrityError, transaction
from backend.core.graphql.types import RoomType, RoomVisibilityEnum
from backend.core.graphql.utils import format_form_errors

from backend.core.models import Room, Topic, Participant, Role
from backend.core.forms import RoomForm
from backend.core.roles import create_default_roles, RoleCode
from backend.core.permissions import has_permission, PermissionCode

class CreateRoom(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        topic_names = graphene.List(graphene.String, required=True)
        description = graphene.String(required=True)
        visibility = RoomVisibilityEnum(required=True)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info: graphene.ResolveInfo, name: str, topics: list[str], description: str, visibility: Room.Visibility):
        data = {
            "name": name,
            "description": description,
            "visibility": visibility,
        }
        
        form = RoomForm(data=data)
        
        if not form.is_valid():
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})
        
        try:
            with transaction.atomic():
                room = form.save(commit=False)
                room.host = info.context.user
                room.save()
                
                topics = [Topic.objects.get_or_create(name=topic_name)[0] for topic_name in topics]
                room.topics.set(topics)
                
                create_default_roles(room)
                
                owner_role = room.roles.get(code=RoleCode.OWNER, room=room)
                
                room.default_role = room.roles.get(code=RoleCode.MEMBER, room=room)
                room.save()
                
                Participant.objects.create(
                    user=info.context.user,
                    room=room,
                    role=owner_role
                )
        except IntegrityError:
            raise GraphQLError(
                "Could not create room due to a conflict.",
                extensions={"code": "CONFLICT"},
            )
        
        return CreateRoom(room=room)


class UpdateRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        topics = graphene.List(graphene.String, required=False)
        visibility = RoomVisibilityEnum(required=False)
        default_role_id = graphene.UUID(required=False)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        topics: Optional[list[str]] = None,
        visibility: Optional[Room.Visibility] = None,
        default_role_id: Optional[uuid.UUID] = None,
    ):
        try:
            room = Room.objects.get(
                id=room_id,
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        if not has_permission(
            info.context.user,
            room,
            PermissionCode.ROOM_UPDATE
        ):
            raise GraphQLError("Permission denied", extensions={"code": "PERMISSION_DENIED"})
        
        data = {}
        
        if name is not None:
            data["name"] = name

        if description is not None:
            data["description"] = description

        if visibility is not None:
            data["visibility"] = visibility
            
        if default_role_id:
            try:
                data["default_role"] = room.roles.get(id=default_role_id, room=room)
            except Role.DoesNotExist:
                raise GraphQLError("Role not found", extensions={"code": "NOT_FOUND"})
        
        with transaction.atomic():
            if topics:
                topics = [
                    Topic.objects.get_or_create(name=topic_name)[0] for topic_name in topics
                ]
                room.topics.set(topics)
                
            form = RoomForm(
                data=data,
                instance=room
            )
            
            if not form.is_valid():
                raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})

            try:
                form.save()
            except IntegrityError:
                raise GraphQLError(
                    "Could not update room due to a conflict.",
                    extensions={"code": "CONFLICT"},
                )
        return UpdateRoom(room=room)

    

class DeleteRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info: graphene.ResolveInfo, room_id: uuid.UUID):
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
    def mutate(self, info: graphene.ResolveInfo, room_id: uuid.UUID) -> "JoinRoom":
        try:
            room = Room.objects.get(
                id=room_id,
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        if Participant.objects.filter(user=info.context.user, room=room).exists():
            raise GraphQLError(
                "Already a participant of this room",
                extensions={"code": "ALREADY_JOINED"}
            )

        Participant.objects.create(
            user=info.context.user,
            room=room,
            role=room.default_role
        )
        
        return JoinRoom(room=room)


class RoomMutation(graphene.ObjectType):
    create_room = CreateRoom.Field()
    delete_room = DeleteRoom.Field()
    update_room = UpdateRoom.Field()
    join_room = JoinRoom.Field()
