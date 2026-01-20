import uuid
import graphene
from typing import Optional, Any
from graphql import GraphQLError

from django.db.models import Q, Count, QuerySet, Prefetch, Exists, OuterRef

from backend.access.models import Participant
from backend.core.exceptions import ErrorCode
from backend.account.models import User
from backend.graphql.room.filters import RoomFilter
from backend.room.models import Room, Topic
from backend.room.services import RoomService
from backend.graphql.room.types import RoomType, TopicType


class RoomQuery(graphene.ObjectType):
    room = graphene.Field(RoomType, room_id=graphene.UUID(required=True))
    rooms = graphene.List(
        RoomType,
        host_slug=graphene.String(),
        search=graphene.String(),
        topics=graphene.List(graphene.String),
    )
    rooms_participated_by_user = graphene.List(
        RoomType, user_slug=graphene.String(required=True)
    )
    rooms_not_participated_by_user = graphene.List(
        RoomType, user_slug=graphene.String(required=True)
    )

    def resolve_room(self, info: graphene.ResolveInfo, room_id: uuid.UUID) -> Room:
        try:
            room = (
                Room.objects.select_related("host")
                .prefetch_related(
                    "topics",
                    Prefetch(
                        "memberships",
                        queryset=Participant.objects.select_related("user", "role"),
                    ),
                )
                .get(id=room_id)
            )
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        if not RoomService.can_view(info.context.user, room):
            raise GraphQLError(
                "Permission denied", extensions={"code": ErrorCode.PERMISSION_DENIED}
            )

        return room

    def resolve_rooms(
        self,
        info: graphene.ResolveInfo,
        host_slug: Optional[str] = None,
        search: Optional[str] = None,
        topics: Optional[list[str]] = None,
    ) -> QuerySet[Room]:
        filters: Any = Q(visibility=Room.Visibility.PUBLIC)

        if info.context.user.is_authenticated:
            filters |= Exists(
                Participant.objects.filter(user=info.context.user, room=OuterRef("pk"))
            )

        queryset = (
            Room.objects.annotate(participants_count=Count("participants"))
            .select_related("host")
            .prefetch_related(
                "topics",
                Prefetch(
                    "memberships",
                    queryset=Participant.objects.select_related("user", "role"),
                ),
            )
            .filter(filters)
        )

        return (
            RoomFilter(
                data={
                    "host_slug": host_slug,
                    "search": search,
                    "topics": topics,
                },
                queryset=queryset,
            )
            .qs.distinct()
            .order_by("-participants_count", "-created_at")
        )

    def resolve_rooms_participated_by_user(
        self, info: graphene.ResolveInfo, user_slug: str
    ) -> QuerySet[Room]:
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        queryset = (
            Room.objects.filter(participants=user)
            .annotate(participants_count=Count("participants"))
            .select_related("host")
            .prefetch_related(
                "topics",
                Prefetch(
                    "memberships",
                    queryset=Participant.objects.select_related("user", "role"),
                ),
            )
            .order_by("-participants_count", "-created_at")
        )

        return queryset

    def resolve_rooms_not_participated_by_user(
        self, info: graphene.ResolveInfo, user_slug: str
    ) -> QuerySet[Room]:
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        queryset = (
            Room.objects.exclude(participants=user)
            .annotate(participants_count=Count("participants"))
            .select_related("host")
            .prefetch_related(
                "topics",
                Prefetch(
                    "memberships",
                    queryset=Participant.objects.select_related("user", "role"),
                ),
            )
            .order_by("-participants_count", "-created_at")
        )

        return queryset


class TopicQuery(graphene.ObjectType):
    topics = graphene.List(
        TopicType, search=graphene.String(), min_rooms=graphene.Int()
    )

    def resolve_topics(
        self,
        info: graphene.ResolveInfo,
        search: Optional[str] = None,
        min_rooms: Optional[int] = None,
    ) -> QuerySet[Topic]:
        queryset = Topic.objects.annotate(room_count=Count("rooms"))

        if search:
            queryset = queryset.filter(name__icontains=search)

        if min_rooms:
            queryset = queryset.filter(room_count__gte=min_rooms)

        return queryset.order_by("-room_count")
