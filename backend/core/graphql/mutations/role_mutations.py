import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.core.graphql.types import RoleType
from backend.core.exceptions import ConflictException, PermissionException, FormValidationException, ErrorCode
from backend.core.models import Role, Room
from backend.core.services.role_service import RoleService


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
        except (PermissionException, ConflictException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})


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
        except (PermissionException, ConflictException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})


class DeleteRole(graphene.Mutation):
    class Arguments:
        role_id = graphene.UUID(required=True)
        substitution_role_id = graphene.UUID(required=False)

    success = graphene.Boolean()

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        role_id: uuid.UUID,
        substitution_role_id: Optional[uuid.UUID] = None,
    ):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found", extensions={"code": "NOT_FOUND"})
        
        substitution_role = None
        if substitution_role_id:
            try:
                substitution_role = Role.objects.get(id=substitution_role_id)
            except Role.DoesNotExist:
                raise GraphQLError("Substitution role not found", extensions={"code": "NOT_FOUND"})
        
        try:
            RoleService.delete_role(
                user=info.context.user,
                role=role,
                substitution_role=substitution_role,
            )
            return DeleteRole(success=True)
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})


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
            raise GraphQLError("Role not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            role = RoleService.assign_permissions_to_role(
                user=info.context.user,
                role=role,
                permission_ids=permission_ids,
            )
            return AssignPermissionsToRole(role=role)
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})


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
            raise GraphQLError("Role not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            role = RoleService.remove_permissions_from_role(
                user=info.context.user,
                role=role,
                permission_ids=permission_ids,
            )
            return RemovePermissionsFromRole(role=role)
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})


class RoleMutation(graphene.ObjectType):
    create_role = CreateRole.Field()
    update_role = UpdateRole.Field()
    delete_role = DeleteRole.Field()
    assign_permissions_to_role = AssignPermissionsToRole.Field()
    remove_permissions_from_role = RemovePermissionsFromRole.Field()
