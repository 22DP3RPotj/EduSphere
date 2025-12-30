import graphene
import uuid
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.graphql.access.types import ParticipantType
from backend.core.models import Room, User
from backend.access.models import Participant, Role
from backend.core.services import ParticipantService
from backend.core.exceptions import (
    PermissionException,
    ValidationException,
    ConflictException,
    ErrorCode
)


class AddParticipant(graphene.Mutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        user_id = graphene.UUID(required=True)
        role_id = graphene.UUID(required=True)

    participant = graphene.Field(ParticipantType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found", extensions={"code": ErrorCode.NOT_FOUND})

        try:
            participant = ParticipantService.add_participant(
                room=room,
                user=user,
                role=role
            )
        except ValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except ConflictException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return AddParticipant(participant=participant)


class ChangeParticipantRole(graphene.Mutation):
    class Arguments:
        participant_id = graphene.UUID(required=True)
        role_id = graphene.UUID(required=True)

    participant = graphene.Field(ParticipantType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        participant_id: uuid.UUID,
        role_id: uuid.UUID,
    ):
        try:
            participant = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            raise GraphQLError("Participant not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError("Role not found", extensions={"code": ErrorCode.NOT_FOUND})

        try:
            participant = ParticipantService.change_participant_role(
                user=info.context.user,
                participant=participant,
                new_role=role
            )
        except (PermissionException, ValidationException) as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return ChangeParticipantRole(participant=participant)


class RemoveParticipant(graphene.Mutation):
    class Arguments:
        participant_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        participant_id: uuid.UUID,
    ):
        try:
            participant = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            raise GraphQLError("Participant not found", extensions={"code": ErrorCode.NOT_FOUND})

        try:
            success = ParticipantService.remove_participant(
                user=info.context.user,
                participant=participant
            )
        except PermissionException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

        return RemoveParticipant(success=success)

