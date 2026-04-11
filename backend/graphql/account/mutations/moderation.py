import graphene
import uuid
from datetime import datetime
from typing import Any, Optional, Self
from graphql import GraphQLError
from graphql_jwt.decorators import superuser_required

from backend.account.models import User
from backend.core.exceptions import ErrorCode
from backend.graphql.mutations import BaseMutation
from backend.account.services import ModerationService


class BanUser(BaseMutation):
    """
    Ban a user.
    """

    class Arguments:
        user_id = graphene.UUID(required=True)
        reason = graphene.String(required=False)
        expires_at = graphene.DateTime(required=False)

    success = graphene.Boolean()

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        user_id: uuid.UUID,
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Self:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        ModerationService.ban_user(
            user=user,
            banned_by=info.context.user,
            reason=reason,
            expires_at=expires_at,
        )
        return cls(success=True)


class UnbanUser(BaseMutation):
    """
    Lift all active bans for a user, skipping if not currently banned.
    """

    class Arguments:
        user_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        user_id: uuid.UUID,
    ) -> Self:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        ModerationService.unban_user(
            actor=info.context.user,
            user=user,
        )
        return cls(success=True)


class BanUsers(BaseMutation):
    """
    Ban one or more users. Skips already-banned users and the actor themselves.
    """

    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)
        reason = graphene.String(required=False)
        expires_at = graphene.DateTime(required=False)

    success = graphene.Boolean()
    banned_count = graphene.Int()
    skipped_count = graphene.Int()

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        user_ids: list[uuid.UUID],
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Self:
        banned, skipped = ModerationService.ban_users(
            actor=info.context.user,
            user_ids=user_ids,
            reason=reason,
            expires_at=expires_at,
        )
        return cls(success=True, banned_count=banned, skipped_count=skipped)


class UnbanUsers(BaseMutation):
    """
    Lift all active bans for one or more users. Skips non-banned users.
    """

    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)

    success = graphene.Boolean()
    unbanned_count = graphene.Int()
    skipped_count = graphene.Int()

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        user_ids: list[uuid.UUID],
    ) -> Self:
        unbanned, skipped = ModerationService.unban_users(
            actor=info.context.user,
            user_ids=user_ids,
        )
        return cls(success=True, unbanned_count=unbanned, skipped_count=skipped)


class PromoteUsers(BaseMutation):
    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)

    success = graphene.Boolean()
    updated_count = graphene.Int()

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        user_ids: list[uuid.UUID],
    ) -> Self:
        updated_count = ModerationService.set_staff_status(
            actor=info.context.user,
            user_ids=user_ids,
            is_staff=True,
        )
        return cls(success=True, updated_count=updated_count)


class DemoteUsers(BaseMutation):
    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)

    success = graphene.Boolean()
    updated_count = graphene.Int()

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        user_ids: list[uuid.UUID],
    ) -> Self:
        updated_count = ModerationService.set_staff_status(
            actor=info.context.user,
            user_ids=user_ids,
            is_staff=False,
        )
        return cls(success=True, updated_count=updated_count)
