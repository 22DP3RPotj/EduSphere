import graphene
import uuid
from typing import Optional, Self, Any
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.core.exceptions import ErrorCode
from backend.graphql.room.types import RoomType, RoomVisibilityEnum
from backend.room.choices import VisibilityChoices
from backend.room.models import Room
from backend.room.services import RoomService
from backend.graphql.mutations import BaseMutation


class CreateRoom(BaseMutation):
    class Arguments:
        name = graphene.String(required=True)
        topic_names = graphene.List(graphene.String, required=True)
        description = graphene.String(required=True)
        visibility = RoomVisibilityEnum(required=False)

    room = graphene.Field(RoomType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        name: str,
        topic_names: list[str],
        description: str,
        visibility: Optional[VisibilityChoices] = None,
    ) -> Self:

        room = RoomService.create_room(
            user=info.context.user,
            name=name,
            description=description,
            visibility=visibility,
            topic_names=topic_names,
        )

        return cls(room=room)


class UpdateRoom(BaseMutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        topic_names = graphene.List(graphene.String, required=False)
        visibility = RoomVisibilityEnum(required=False)

    room = graphene.Field(RoomType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        topic_names: Optional[list[str]] = None,
        visibility: Optional[VisibilityChoices] = None,
    ) -> Self:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        room = RoomService.update_room(
            user=info.context.user,
            room=room,
            name=name,
            description=description,
            visibility=visibility,
            topic_names=topic_names,
        )

        return cls(room=room)


class DeleteRoom(BaseMutation):
    class Arguments:
        room_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @classmethod
    @login_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, room_id: uuid.UUID
    ) -> Self:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        success = RoomService.delete_room(user=info.context.user, room=room)

        return cls(success=success)


class JoinRoom(BaseMutation):
    class Arguments:
        room_id = graphene.UUID(required=True)

    room = graphene.Field(RoomType)

    @classmethod
    @login_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, room_id: uuid.UUID
    ) -> Self:
        try:
            room = Room.objects.get(
                id=room_id,
            )
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        RoomService.join_room(user=info.context.user, room=room)

        return cls(room=room)


class LeaveRoom(BaseMutation):
    class Arguments:
        room_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @classmethod
    @login_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, room_id: uuid.UUID
    ) -> Self:
        try:
            room = Room.objects.get(
                id=room_id,
            )
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        success = RoomService.leave_room(user=info.context.user, room=room)

        return cls(success=success)
