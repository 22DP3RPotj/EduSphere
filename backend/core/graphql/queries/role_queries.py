import graphene
import uuid
from graphql import GraphQLError

from django.db.models import QuerySet

from backend.core.graphql.types import RoleType
from backend.core.models import Role, Room
from backend.core.services.role_service import RoleService


class RoleQuery(graphene.ObjectType):
    role = graphene.Field(
        RoleType,
        role_id=graphene.UUID(required=True),
    )
    room_roles = graphene.List(
        RoleType,
        room_id=graphene.UUID(required=True),
    )
    
    def resolve_role(self, info: graphene.ResolveInfo, role_id: uuid.UUID) -> Role:
        role = RoleService.get_role_by_id(role_id)
        if not role:
            raise GraphQLError("Role not found", extensions={"code": "NOT_FOUND"})
        return role

    def resolve_room_roles(self, info: graphene.ResolveInfo, room_id: uuid.UUID) -> QuerySet[Role]:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        return RoleService.get_room_roles(room)
