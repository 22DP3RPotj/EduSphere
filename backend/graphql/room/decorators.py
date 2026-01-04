from graphql import GraphQLError
from functools import wraps
from backend.access.services import RoleService
from backend.room.models import Room
from backend.core.exceptions import ErrorCode


def require_room_permission(perm_code, room_arg="room_id"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, info, *args, **kwargs):
            user = info.context.user
            room_id = kwargs.get(room_arg)

            if not room_id:
                raise GraphQLError(
                    f"Missing required argument: {room_arg}",
                    extensions={"code": ErrorCode.BAD_REQUEST},
                )

            if not user.is_authenticated:
                raise GraphQLError(
                    "Authentication required",
                    extensions={"code": ErrorCode.PERMISSION_DENIED},
                )

            try:
                room = Room.objects.get(id=room_id)
            except Room.DoesNotExist:
                raise GraphQLError(
                    "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
                )

            if not RoleService.has_permission(info.context.user, room, perm_code):
                raise GraphQLError(
                    f"Permission denied. Expected '{perm_code}' permission",
                    extensions={"code": ErrorCode.PERMISSION_DENIED},
                )

            kwargs["room"] = room
            return func(self, info, *args, **kwargs)

        return wrapper

    return decorator
