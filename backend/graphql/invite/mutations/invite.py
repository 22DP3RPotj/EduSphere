import graphene
import uuid
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.graphql.invite.types import InviteType
from backend.graphql.access.types import ParticipantType
from backend.core.models import User
from backend.room.models import Room
from backend.access.models import Role
from backend.invite.services import InviteService
from backend.core.exceptions import (
    PermissionException,
    FormValidationException,
    ConflictException,
    ValidationException,
    ErrorCode
)


class SendInvite(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        role_id = graphene.UUID(required=True)
        invitee_id = graphene.UUID(required=True)
        expires_at = graphene.DateTime(required=True)
        
    invite = graphene.Field(InviteType)
    
    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        role_id: uuid.UUID,
        invitee_id: uuid.UUID,
        expires_at: graphene.DateTime
    ):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            invitee = User.objects.get(id=invitee_id)
        except User.DoesNotExist:
            raise GraphQLError("Invitee not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found in the specified room", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            invite = InviteService.send_invite(
                inviter=info.context.user,
                room=room,
                invitee=invitee,
                role=role,
                expires_at=expires_at
            )
        except (PermissionException, ValidationException, ConflictException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})

        return SendInvite(invite=invite)
                

class AcceptInvite(graphene.Mutation):
    class Arguments:
        token = graphene.UUID(required=True)
        
    participant = graphene.Field(ParticipantType)
    
    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        token: uuid.UUID
    ):
        invite = InviteService.get_invite_by_token(token=token)
        
        if invite is None:
            raise GraphQLError(f"Invite with token '{token}' not found.", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            participant = InviteService.accept_invite(
                user=info.context.user,
                invite=invite
            )
        except (PermissionException, ValidationException, ConflictException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return AcceptInvite(participant=participant)


class DeclineInvite(graphene.Mutation):
    class Arguments:
        token = graphene.UUID(required=True)
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info: graphene.ResolveInfo, token: uuid.UUID):
        invite = InviteService.get_invite_by_token(token)
        
        if invite is None:
            raise GraphQLError(f"Invite with token '{token}' not found.", extensions={"code": ErrorCode.NOT_FOUND})
        
        if invite.invitee != info.context.user:
            raise GraphQLError("You are not the invitee for this invite.", extensions={"code": ErrorCode.PERMISSION_DENIED})
        
        try:
            success = InviteService.decline_invite(
                user=info.context.user,
                invite=invite
            )
        except (PermissionException, ValidationException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return DeclineInvite(success=success)


class CancelInvite(graphene.Mutation):
    class Arguments:
        token = graphene.UUID(required=True)
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info: graphene.ResolveInfo, token: uuid.UUID):
        invite = InviteService.get_invite_by_token(token)
        
        if invite is None:
            raise GraphQLError(f"Invite with token '{token}' not found.", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            success = InviteService.cancel_invite(
                user=info.context.user,
                invite=invite
            )
        except (PermissionException, ValidationException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return CancelInvite(success=success)


class ResendInvite(graphene.Mutation):
    class Arguments:
        token = graphene.UUID(required=True)
        expires_at = graphene.DateTime()
        
    invite = graphene.Field(InviteType)
    
    @login_required
    def mutate(self, info: graphene.ResolveInfo, token: uuid.UUID, expires_at: graphene.DateTime):
        invite = InviteService.get_invite_by_token(token)
        
        if invite is None:
            raise GraphQLError(f"Invite with token '{token}' not found.", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            invite = InviteService.resend_invite(
                user=info.context.user,
                invite=invite,
                new_expires_at=expires_at
            )
        except (PermissionException, ValidationException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return ResendInvite(invite=invite)