import uuid

import graphene
from django.db.models import QuerySet
from graphql import GraphQLError

from django.db.models import QuerySet, Count, Q

from backend.access.models import Participant
from backend.account.models import User
from backend.core.exceptions import ErrorCode
from backend.graphql.messaging.types import MessageType
from backend.messaging.models import Message
from backend.messaging.choices import MessageStatusChoices
from backend.room.models import Room


class MessageQuery(graphene.ObjectType):
    messages = graphene.List(MessageType, room_id=graphene.UUID(required=True))
    messages_by_user = graphene.List(
        MessageType,
        user_id=graphene.UUID(required=True),
    )

    def resolve_messages(
        self, info: graphene.ResolveInfo, room_id: uuid.UUID
    ) -> QuerySet[Message]:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            ) from None

        if not Participant.objects.filter(user=info.context.user, room=room).exists():
            raise GraphQLError(
                "Not a participant", extensions={"code": ErrorCode.PERMISSION_DENIED}
            )

        qs = (
            room.message_set.select_related("author", "parent", "parent__author")
            .annotate(
                _status_delivered=Count(
                    "statuses",
                    filter=Q(statuses__status=MessageStatusChoices.DELIVERED),
                ),
                _status_seen=Count(
                    "statuses",
                    filter=Q(statuses__status=MessageStatusChoices.SEEN),
                ),
            )
            .order_by("created_at")
        )
        return qs

    def resolve_messages_by_user(
        self, info: graphene.ResolveInfo, user_id: uuid.UUID
    ) -> QuerySet[Message]:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            ) from None

        return user.message_set.select_related("room", "room__host").order_by(
            "-created_at"
        )
