import graphene
import uuid
from typing import Optional, Any, Self
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from backend.graphql.access.types import RoleType, RoleDeleteType
from backend.core.exceptions import ErrorCode

from backend.graphql.base import BaseMutation
from backend.room.models import Room
from backend.access.models import Role
from backend.access.services import RoleService


class CreateRole(BaseMutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        priority = graphene.Int(required=True)
        permission_ids = graphene.List(graphene.UUID, required=False)

    role = graphene.Field(RoleType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        name: str,
        description: str,
        priority: int,
        permission_ids: list[uuid.UUID],
    ) -> Self:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        role = RoleService.create_role(
            user=info.context.user,
            room=room,
            name=name,
            description=description,
            priority=priority,
            permission_ids=permission_ids,
        )

        return cls(role=role)


class UpdateRole(BaseMutation):
    class Arguments:
        role_id = graphene.UUID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        priority = graphene.Int(required=False)
        permission_ids = graphene.List(graphene.UUID, required=False)

    role = graphene.Field(RoleType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        role_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        permission_ids: Optional[list[uuid.UUID]] = None,
    ) -> Self:
        role = RoleService.get_role_by_id(role_id=role_id)

        if role is None:
            raise GraphQLError(
                "Role not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        role = RoleService.update_role(
            user=info.context.user,
            role=role,
            name=name,
            description=description,
            priority=priority,
            permission_ids=permission_ids,
        )

        return cls(role=role)


class DeleteRole(BaseMutation):
    class Arguments:
        role_id = graphene.UUID(required=True)
        substitution_role_id = graphene.UUID(required=False)

    result = graphene.Field(RoleDeleteType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        role_id: uuid.UUID,
        substitution_role_id: Optional[uuid.UUID] = None,
    ) -> Self:
        role = RoleService.get_role_by_id(role_id=role_id)

        if role is None:
            raise GraphQLError(
                "Role not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        # TODO: Move to service
        substitution_role = None
        if substitution_role_id:
            try:
                substitution_role = Role.objects.get(id=substitution_role_id)
            except Role.DoesNotExist:
                raise GraphQLError(
                    "Substitution role not found",
                    extensions={"code": ErrorCode.NOT_FOUND},
                )

        result = RoleService.delete_role(
            user=info.context.user,
            role=role,
            substitution_role=substitution_role,
        )

        return cls(result=result)


class AssignPermissionsToRole(BaseMutation):
    class Arguments:
        role_id = graphene.UUID(required=True)
        permission_ids = graphene.List(graphene.UUID, required=True)

    role = graphene.Field(RoleType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        role_id: uuid.UUID,
        permission_ids: list[uuid.UUID],
    ) -> Self:
        role = RoleService.get_role_by_id(role_id=role_id)

        if role is None:
            raise GraphQLError(
                "Role not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        role = RoleService.assign_permissions_to_role(
            user=info.context.user,
            role=role,
            permission_ids=permission_ids,
        )

        return cls(role=role)


class RemovePermissionsFromRole(BaseMutation):
    class Arguments:
        role_id = graphene.UUID(required=True)
        permission_ids = graphene.List(graphene.UUID, required=True)

    role = graphene.Field(RoleType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        role_id: uuid.UUID,
        permission_ids: list[uuid.UUID],
    ) -> Self:
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError(
                "Role not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        role = RoleService.remove_permissions_from_role(
            user=info.context.user,
            role=role,
            permission_ids=permission_ids,
        )

        return cls(role=role)
