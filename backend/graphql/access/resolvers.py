import graphene
import uuid
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from django.db.models import QuerySet

from backend.core.exceptions import ErrorCode
from backend.graphql.access.types import PermissionType, RoleType
from backend.room.models import Room
from backend.access.services import RoleService
from backend.access.models import Permission, Role


class RoleQuery(graphene.ObjectType):
    role = graphene.Field(
        RoleType,
        role_id=graphene.UUID(required=True),
    )
    room_roles = graphene.List(
        RoleType,
        room_id=graphene.UUID(required=True),
    )
    available_permissions = graphene.List(
        PermissionType,
        room_id=graphene.UUID(required=True),
    )

    def resolve_role(self, info: graphene.ResolveInfo, role_id: uuid.UUID) -> Role:
        role = RoleService.get_role_by_id(role_id)

        if role is None:
            raise GraphQLError(
                "Role not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        return role

    def resolve_room_roles(
        self, info: graphene.ResolveInfo, room_id: uuid.UUID
    ) -> QuerySet[Role]:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        return Role.objects.by_room(room).with_permissions()

    @login_required
    def resolve_available_permissions(
        self, info: graphene.ResolveInfo, room_id: uuid.UUID
    ) -> QuerySet[Permission]:
        user = info.context.user

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        participant = RoleService.get_participant(user, room)

        if participant is None:
            return Permission.objects.none()

        return Permission.objects.visible_to(participant)
