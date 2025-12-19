import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from django.db import IntegrityError

from backend.core.graphql.types import RoleType
from backend.core.graphql.utils import format_form_errors
from backend.core.models import Role, Room
from backend.core.services.role import RoleService


class CreateRole(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        priority = graphene.Int(required=True)
        permission_ids = graphene.List(graphene.UUID, required=False)

    role = graphene.Field(RoleType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        name: str,
        description: str,
        priority: int,
        permission_ids: Optional[list[uuid.UUID]] = None,
    ):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        try:
            role = RoleService.create_role(
                user=info.context.user,
                room=room,
                name=name,
                description=description,
                priority=priority,
                permission_ids=permission_ids,
            )
            return CreateRole(role=role)
        except PermissionError as e:
            raise GraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})
        except ValueError as e:
            raise GraphQLError(str(e), extensions={"code": "VALIDATION_ERROR"})
        except IntegrityError as e:
            raise GraphQLError(
                "Could not create role due to a conflict.",
                extensions={"code": "CONFLICT"},
            )


class UpdateRole(graphene.Mutation):
    class Arguments:
        role_id = graphene.UUID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        priority = graphene.Int(required=False)
        permission_ids = graphene.List(graphene.UUID, required=False)

    role = graphene.Field(RoleType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        role_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        permission_ids: Optional[list[uuid.UUID]] = None,
    ):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found", extensions={"code": "NOT_FOUND"})
        
        try:
            role = RoleService.update_role(
                user=info.context.user,
                role=role,
                name=name,
                description=description,
                priority=priority,
                permission_ids=permission_ids,
            )
            return UpdateRole(role=role)
        except PermissionError as e:
            raise GraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})
        except ValueError as e:
            raise GraphQLError(str(e), extensions={"code": "VALIDATION_ERROR"})
        except IntegrityError as e:
            raise GraphQLError(
                "Could not update role due to a conflict.",
                extensions={"code": "CONFLICT"},
            )


class DeleteRole(graphene.Mutation):
    class Arguments:
        role_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info: graphene.ResolveInfo, role_id: uuid.UUID):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found", extensions={"code": "NOT_FOUND"})
        
        try:
            RoleService.delete_role(user=info.context.user, role=role)
            return DeleteRole(success=True)
        except PermissionError as e:
            raise GraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})
        except ValueError as e:
            raise GraphQLError(str(e), extensions={"code": "VALIDATION_ERROR"})


class AssignPermissionsToRole(graphene.Mutation):
    class Arguments:
        role_id = graphene.UUID(required=True)
        permission_ids = graphene.List(graphene.UUID, required=True)

    role = graphene.Field(RoleType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        role_id: uuid.UUID,
        permission_ids: list[uuid.UUID],
    ):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found", extensions={"code": "NOT_FOUND"})
        
        try:
            role = RoleService.assign_permissions_to_role(
                user=info.context.user,
                role=role,
                permission_ids=permission_ids,
            )
            return AssignPermissionsToRole(role=role)
        except PermissionError as e:
            raise GraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})


class RemovePermissionsFromRole(graphene.Mutation):
    class Arguments:
        role_id = graphene.UUID(required=True)
        permission_ids = graphene.List(graphene.UUID, required=True)

    role = graphene.Field(RoleType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        role_id: uuid.UUID,
        permission_ids: list[uuid.UUID],
    ):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found", extensions={"code": "NOT_FOUND"})
        
        try:
            role = RoleService.remove_permissions_from_role(
                user=info.context.user,
                role=role,
                permission_ids=permission_ids,
            )
            return RemovePermissionsFromRole(role=role)
        except PermissionError as e:
            raise GraphQLError(str(e), extensions={"code": "PERMISSION_DENIED"})


class RoleMutation(graphene.ObjectType):
    create_role = CreateRole.Field()
    update_role = UpdateRole.Field()
    delete_role = DeleteRole.Field()
    assign_permissions_to_role = AssignPermissionsToRole.Field()
    remove_permissions_from_role = RemovePermissionsFromRole.Field()
