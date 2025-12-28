import graphene
import uuid
from typing import Optional
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.db.models import QuerySet

from backend.core.exceptions import ErrorCode
from backend.core.graphql.types import InviteStatusEnum, InviteType
from backend.core.models import Invite


class InviteQuery(graphene.ObjectType):
    my_invites = graphene.List(InviteType)
    invite = graphene.Field(
        InviteType,
        token=graphene.UUID(required=True)
    )
    all_invites = graphene.List(
        InviteType,
        status=InviteStatusEnum(required=False),
        inviter=graphene.UUID(required=False),
        invitee=graphene.UUID(required=False),
    )
    invite_count = graphene.Int(
        status=InviteStatusEnum(required=False),
        inviter=graphene.UUID(required=False),
        invitee=graphene.UUID(required=False),
    )

    @login_required
    def resolve_my_invites(self, info: graphene.ResolveInfo) -> QuerySet[Invite]:
        return Invite.objects.filter(invitee=info.context.user).select_related('inviter', 'invitee', 'role')

    @login_required
    def resolve_invite(self, info: graphene.ResolveInfo, token: uuid.UUID) -> Invite:
        try:
            invite = Invite.objects.select_related('inviter', 'invitee', 'role').get(token=token)
        except Invite.DoesNotExist:
            raise GraphQLError("Invite not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        if invite.invitee != info.context.user and invite.inviter != info.context.user:
            raise GraphQLError("Permission denied", extensions={"code": ErrorCode.PERMISSION_DENIED})
        
        return invite

    # TODO: Add pagination
    @superuser_required
    def resolve_all_invites(
        self,
        info: graphene.ResolveInfo,
        status: Optional[Invite.InviteStatus] = None,
        invitee_id: Optional[uuid.UUID] = None,
        inviter_id: Optional[uuid.UUID] = None
    ) -> QuerySet[Invite]:
        queryset = Invite.objects.select_related('inviter', 'invitee', 'role')
        
        if status:
            queryset = queryset.filter(status=status)
        if invitee_id:
            queryset = queryset.filter(invitee_id=invitee_id)
        if inviter_id:
            queryset = queryset.filter(inviter_id=inviter_id)

        return queryset
    
    @superuser_required
    def resolve_invite_count(
        self,
        info: graphene.ResolveInfo,
        status: Optional[Invite.InviteStatus] = None,
        invitee_id: Optional[uuid.UUID] = None,
        inviter_id: Optional[uuid.UUID] = None
    ) -> int:
        return self.resolve_all_invites(info, status=status, invitee_id=invitee_id, inviter_id=inviter_id).count()
