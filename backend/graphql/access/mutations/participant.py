import graphene
import uuid
from typing import Optional, Any, Self
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.graphql.access.types import ParticipantType
from backend.account.models import User
from backend.graphql.mutations import BaseMutation
from backend.room.models import Room
from backend.access.models import Participant, Role
from backend.access.services import ParticipantService
from backend.core.exceptions import ErrorCode


class AddParticipant(BaseMutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        user_id = graphene.UUID(required=True)
        role_id = graphene.UUID(required=True)

    participant = graphene.Field(ParticipantType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> Self:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError(
                "Role not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        participant = ParticipantService.add_participant(
            room=room, user=user, role=role
        )

        return cls(participant=participant)


class ChangeParticipantRole(BaseMutation):
    class Arguments:
        participant_id = graphene.UUID(required=True)
        role_id = graphene.UUID(required=True)

    participant = graphene.Field(ParticipantType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        participant_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> Self:
        try:
            participant = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            raise GraphQLError(
                "Participant not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise GraphQLError(
                "Role not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        participant = ParticipantService.change_participant_role(
            user=info.context.user, participant=participant, new_role=role
        )

        return cls(participant=participant)


class RemoveParticipant(BaseMutation):
    class Arguments:
        participant_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        participant_id: uuid.UUID,
    ) -> Self:
        try:
            participant = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            raise GraphQLError(
                "Participant not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        success = ParticipantService.remove_participant(
            user=info.context.user, participant=participant
        )

        return cls(success=success)
