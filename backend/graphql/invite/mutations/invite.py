import graphene
import uuid
from typing import Optional, Any, Self
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

from backend.graphql.base import BaseMutation
from backend.graphql.invite.types import InviteType
from backend.graphql.access.types import ParticipantType
from backend.account.models import User
from backend.room.models import Room
from backend.access.models import Role
from backend.invite.services import InviteService
from backend.core.exceptions import ErrorCode


class SendInvite(BaseMutation):
    class Arguments:
        room_id = graphene.UUID(required=True)
        invitee_id = graphene.UUID(required=True)
        expires_at = graphene.DateTime(required=True)
        role_id = graphene.UUID(required=False)

    invite = graphene.Field(InviteType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        room_id: uuid.UUID,
        invitee_id: uuid.UUID,
        expires_at: graphene.DateTime,
        role_id: Optional[uuid.UUID] = None,
    ) -> Self:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        try:
            invitee = User.objects.get(id=invitee_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "Invitee not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        role = None
        if role_id is not None:
            try:
                role = Role.objects.get(id=role_id, room=room)
            except Role.DoesNotExist:
                raise GraphQLError(
                    "Role not found in the specified room",
                    extensions={"code": ErrorCode.NOT_FOUND},
                )

        invite = InviteService.send_invite(
            inviter=info.context.user,
            room=room,
            invitee=invitee,
            role=role,
            expires_at=expires_at,
        )

        return cls(invite=invite)


class AcceptInvite(BaseMutation):
    class Arguments:
        token = graphene.UUID(required=True)

    participant = graphene.Field(ParticipantType)

    @classmethod
    @login_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, token: uuid.UUID
    ) -> Self:
        invite = InviteService.get_invite_by_token(token=token)

        if invite is None:
            raise GraphQLError(
                f"Invite with token '{token}' not found.",
                extensions={"code": ErrorCode.NOT_FOUND},
            )

        participant = InviteService.accept_invite(user=info.context.user, invite=invite)

        return cls(participant=participant)


class DeclineInvite(BaseMutation):
    class Arguments:
        token = graphene.UUID(required=True)

    invite = graphene.Field(InviteType)

    @classmethod
    @login_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, token: uuid.UUID
    ) -> Self:
        invite = InviteService.get_invite_by_token(token)

        if invite is None:
            raise GraphQLError(
                f"Invite with token '{token}' not found.",
                extensions={"code": ErrorCode.NOT_FOUND},
            )

        invite = InviteService.decline_invite(user=info.context.user, invite=invite)

        return cls(invite=invite)


class CancelInvite(BaseMutation):
    class Arguments:
        token = graphene.UUID(required=True)

    invite = graphene.Field(InviteType)

    @classmethod
    @login_required
    def resolve(
        cls, root: Optional[Any], info: graphene.ResolveInfo, token: uuid.UUID
    ) -> Self:
        invite = InviteService.get_invite_by_token(token)

        if invite is None:
            raise GraphQLError(
                f"Invite with token '{token}' not found.",
                extensions={"code": ErrorCode.NOT_FOUND},
            )

        invite = InviteService.cancel_invite(user=info.context.user, invite=invite)

        return cls(invite=invite)


class ResendInvite(BaseMutation):
    class Arguments:
        token = graphene.UUID(required=True)
        expires_at = graphene.DateTime(required=False)

    invite = graphene.Field(InviteType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        token: uuid.UUID,
        expires_at: graphene.DateTime,
    ):
        invite = InviteService.get_invite_by_token(token)

        if invite is None:
            raise GraphQLError(
                f"Invite with token '{token}' not found.",
                extensions={"code": ErrorCode.NOT_FOUND},
            )

        invite = InviteService.resend_invite(
            user=info.context.user, invite=invite, new_expires_at=expires_at
        )

        return cls(invite=invite)
