import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.core.graphql.types import RoomType, RoomVisibilityEnum
from backend.core.models import Room, Participant
from backend.core.services import RoomService
from backend.core.exceptions import (
    PermissionException,
    FormValidationException,
    ConflictException,
    ErrorCode
)


class CreateRoom(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        topic_names = graphene.List(graphene.String, required=True)
        description = graphene.String(required=True)
        visibility = RoomVisibilityEnum(required=True)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info: graphene.ResolveInfo, name: str, topic_names: list[str], description: str, visibility: Room.Visibility):
        try:
            room = RoomService.create_room(
                user=info.context.user,
                name=name,
                description=description,
                visibility=visibility,
                topic_names=topic_names,
            )
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})
        except ConflictException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return CreateRoom(room=room)

class UpdateRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        topic_names = graphene.List(graphene.String, required=False)
        visibility = RoomVisibilityEnum(required=False)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        topic_names: Optional[list[str]] = None,
        visibility: Optional[Room.Visibility] = None,
    ):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            room = RoomService.update_room(
                user=info.context.user,
                room=room,
                name=name,
                description=description,
                visibility=visibility,
                topic_names=topic_names,
            )
        except (PermissionException, ConflictException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})

        return UpdateRoom(room=room)
    

class DeleteRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info: graphene.ResolveInfo, room_id: uuid.UUID):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            success = RoomService.delete_room(
                user=info.context.user,
                room=room
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return DeleteRoom(success=success)

class JoinRoom(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)

    room = graphene.Field(RoomType)

    @login_required
    def mutate(self, info: graphene.ResolveInfo, room_id: uuid.UUID):
        try:
            room = Room.objects.get(
                id=room_id,
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        if Participant.objects.filter(user=info.context.user, room=room).exists():
            raise GraphQLError(
                "Already a participant of this room",
                extensions={"code": ErrorCode.PERMISSION_DENIED}
            )
            
        if room.visibility == Room.Visibility.PRIVATE:
            raise GraphQLError(
                "Cannot join a private room",
                extensions={"code": ErrorCode.PERMISSION_DENIED}
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
