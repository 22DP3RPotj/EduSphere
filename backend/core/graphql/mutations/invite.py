import graphene
import uuid
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from django.db import transaction, IntegrityError
from backend.core.graphql.types import InviteType
from backend.core.graphql.utils import format_form_errors
from backend.core.models import Invite, Room, User, Role, Participant, PermissionCode
from backend.core.permissions import has_permission
from backend.core.forms import InviteForm

# TODO: Lazy invite expiration handling + Service layer refactor

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
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        try:
            invitee = User.objects.get(id=invitee_id)
        except User.DoesNotExist:
            raise GraphQLError("Invitee not found", extensions={"code": "NOT_FOUND"})
        
        try:
            role = Role.objects.get(id=role_id, room=room)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found in the specified room", extensions={"code": "NOT_FOUND"})

        if not Participant.objects.filter(user=info.context.user, room=room).exists():
            raise GraphQLError(
                "You must be a participant of the room to report it", 
                extensions={"code": "NOT_PARTICIPANT"}
            )
            
        if Participant.objects.filter(user=invitee, room=room).exists():
            raise GraphQLError(
                "The user is already a participant of the room.",
                extensions={"code": "ALREADY_PARTICIPANT"},
            )
            
        if not has_permission(info.context.user, room, PermissionCode.ROOM_INVITE):
            raise GraphQLError(
                "You do not have permission to invite users to this room.",
                extensions={"code": "FORBIDDEN"},
            )

        if Invite.active_invites(invitee=invitee, room=room).exists():
            raise GraphQLError(
                "You already have an active invite targeting this room.",
                extensions={"code": "ALREADY_INVITED"},
            )
        data = {
            "role": role_id,
            "expires_at": expires_at,
        }
        
        form = InviteForm(data=data)
        
        if not form.is_valid():
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})

        with transaction.atomic():
            invite = form.save(commit=False)
            invite.inviter = info.context.user
            invite.invitee = invitee
            invite.role = role
            invite.room = room
            
            try:
                invite.save()
            except IntegrityError:
                raise GraphQLError(
                    "Could not send invite due to a conflict.",
                    extensions={"code": "CONFLICT"},
                )
                
        return SendInvite(invite=invite)
                

class AcceptInvite(graphene.Mutation):
    class Arguments:
        token = graphene.UUID(required=True)
        
    invite = graphene.Field(InviteType)
    
    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        token: uuid.UUID
    ):
        try:
            invite = Invite.objects.get(token=token, invitee=info.context.user)
        except Invite.DoesNotExist:
            raise GraphQLError("Invite not found", extensions={"code": "NOT_FOUND"})
        
        if invite.status != Invite.InviteStatus.PENDING:
            raise GraphQLError("Invite is not pending", extensions={"code": "INVALID_STATUS"})
        
        if not invite.invitee == info.context.user:
            raise GraphQLError("You are not the invitee for this invite", extensions={"code": "FORBIDDEN"})
        
        with transaction.atomic():
            invite.status = Invite.InviteStatus.ACCEPTED
            invite.save()
                
            try:
                Participant.objects.create(
                    user=info.context.user,
                    room=invite.room,
                    role=invite.role
                )
            except IntegrityError:
                raise GraphQLError(
                    "Could not accept invite due to a conflict.",
                    extensions={"code": "CONFLICT"},
                )
            
        return AcceptInvite(invite=invite)


class DeclineInvite(graphene.Mutation):
    class Arguments:
        token = graphene.UUID(required=True)
        
    invite = graphene.Field(InviteType)
    
    @login_required
    def mutate(self, info: graphene.ResolveInfo, token: uuid.UUID):
        try:
            invite = Invite.objects.get(token=token, invitee=info.context.user)
        except Invite.DoesNotExist:
            raise GraphQLError("Invite not found", extensions={"code": "NOT_FOUND"})
        
        if invite.status != Invite.InviteStatus.PENDING:
            raise GraphQLError("Invite is not pending", extensions={"code": "INVALID_STATUS"})
        
        if not invite.invitee == info.context.user:
            raise GraphQLError("You are not the invitee for this invite", extensions={"code": "FORBIDDEN"})
        
        invite.status = Invite.InviteStatus.DECLINED
        invite.save()
        
        return DeclineInvite(invite=invite)


class InviteMutation(graphene.ObjectType):
    send_invite = SendInvite.Field()
    accept_invite = AcceptInvite.Field()
    decline_invite = DeclineInvite.Field()