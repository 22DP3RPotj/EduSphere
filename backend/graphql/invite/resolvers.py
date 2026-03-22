import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.db.models import QuerySet
from django.utils import timezone

from backend.core.exceptions import ErrorCode
from backend.graphql.invite.types import InviteType, InviteStatusEnum
from backend.graphql.invite.filters import InviteFilter
from backend.invite.choices import InviteStatusChoices
from backend.invite.models import Invite
from backend.invite.services import InviteService


class InviteQuery(graphene.ObjectType):
    received_invites = graphene.List(InviteType)
    sent_invites = graphene.List(InviteType)
    invite = graphene.Field(InviteType, token=graphene.UUID(required=True))
    invites = graphene.List(
        InviteType,
        room=graphene.UUID(),
        inviter=graphene.UUID(),
        invitee=graphene.UUID(),
        status=InviteStatusEnum(),
        is_expired=graphene.Boolean(),
        is_active=graphene.Boolean(),
        created_after=graphene.DateTime(),
        created_before=graphene.DateTime(),
        expires_after=graphene.DateTime(),
        expires_before=graphene.DateTime(),
    )
    invite_count = graphene.Int(
        room=graphene.UUID(),
        inviter=graphene.UUID(),
        invitee=graphene.UUID(),
        status=InviteStatusEnum(),
        is_expired=graphene.Boolean(),
        is_active=graphene.Boolean(),
        created_after=graphene.DateTime(),
        created_before=graphene.DateTime(),
        expires_after=graphene.DateTime(),
        expires_before=graphene.DateTime(),
    )

    @login_required
    def resolve_received_invites(self, info: graphene.ResolveInfo) -> QuerySet[Invite]:
        queryset = Invite.objects.filter(invitee=info.context.user).select_related(
            "inviter", "invitee", "role"
        )

        queryset.filter(
            status=Invite.Status.PENDING, expires_at__lt=timezone.now()
        ).update(status=Invite.Status.EXPIRED)

        return queryset

    @login_required
    def resolve_sent_invites(self, info: graphene.ResolveInfo) -> QuerySet[Invite]:
        queryset = Invite.objects.filter(inviter=info.context.user).select_related(
            "inviter", "invitee", "role"
        )

        queryset.filter(
            status=Invite.Status.PENDING, expires_at__lt=timezone.now()
        ).update(status=Invite.Status.EXPIRED)

        return queryset

    @login_required
    def resolve_invite(self, info: graphene.ResolveInfo, token: uuid.UUID) -> Invite:
        invite = InviteService.get_invite_by_token(token)

        if invite is None:
            raise GraphQLError(
                "Invite not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        if invite.invitee != info.context.user and invite.inviter != info.context.user:
            raise GraphQLError(
                "Permission denied", extensions={"code": ErrorCode.PERMISSION_DENIED}
            )

        return invite

    # TODO: Add pagination
    @superuser_required
    def resolve_invites(
        self,
        info: graphene.ResolveInfo,
        room: Optional[uuid.UUID] = None,
        inviter: Optional[uuid.UUID] = None,
        invitee: Optional[uuid.UUID] = None,
        status: Optional[InviteStatusChoices] = None,
        is_expired: Optional[bool] = None,
        is_active: Optional[bool] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        expires_after: Optional[str] = None,
        expires_before: Optional[str] = None,
    ) -> QuerySet[Invite]:
        queryset = Invite.objects.select_related("inviter", "invitee", "role")
        filter_data = {
            k: v
            for k, v in {
                "room": room,
                "inviter": inviter,
                "invitee": invitee,
                "status": status,
                "is_expired": is_expired,
                "is_active": is_active,
                "created_after": created_after,
                "created_before": created_before,
                "expires_after": expires_after,
                "expires_before": expires_before,
            }.items()
            if v is not None
        }
        return InviteFilter(filter_data, queryset=queryset).qs

    @superuser_required
    def resolve_invite_count(
        self,
        info: graphene.ResolveInfo,
        room: Optional[uuid.UUID] = None,
        inviter: Optional[uuid.UUID] = None,
        invitee: Optional[uuid.UUID] = None,
        status: Optional[InviteStatusChoices] = None,
        is_expired: Optional[bool] = None,
        is_active: Optional[bool] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        expires_after: Optional[str] = None,
        expires_before: Optional[str] = None,
    ) -> int:
        return self.resolve_invites(
            info,
            room=room,
            inviter=inviter,
            invitee=invitee,
            status=status,
            is_expired=is_expired,
            is_active=is_active,
            created_after=created_after,
            created_before=created_before,
            expires_after=expires_after,
            expires_before=expires_before,
        ).count()
