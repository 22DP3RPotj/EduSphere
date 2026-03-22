import uuid
import graphene
from typing import Optional
from graphql import GraphQLError

from django.db.models import QuerySet

from backend.core.exceptions import ErrorCode
from backend.account.models import User
from backend.graphql.room.filters import RoomFilter, TopicFilter
from backend.room.models import Room, Topic
from backend.room.rules.labels import RoomPermission
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
        RoomType, user_id=graphene.UUID(required=True)
    )
    rooms_not_participated_by_user = graphene.List(
        RoomType, user_id=graphene.UUID(required=True)
    )

    def resolve_room(self, info: graphene.ResolveInfo, room_id: uuid.UUID) -> Room:
        try:
            room = Room.objects.with_details().get(id=room_id)
        except Room.DoesNotExist:
            raise GraphQLError(
                "Room not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        if not info.context.user.has_perm(RoomPermission.VIEW, room):
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
        queryset = (
            Room.objects.with_participants_count()
            .with_details()
            .visible_to(info.context.user)
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
            .ordered_by_popularity()
        )

    def resolve_rooms_participated_by_user(
        self, info: graphene.ResolveInfo, user_id: uuid.UUID
    ) -> QuerySet[Room]:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        queryset = (
            Room.objects.participated_by(user)
            .with_participants_count()
            .with_details()
            .ordered_by_popularity()
        )

        return queryset

    def resolve_rooms_not_participated_by_user(
        self, info: graphene.ResolveInfo, user_id: uuid.UUID
    ) -> QuerySet[Room]:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError(
                "User not found", extensions={"code": ErrorCode.NOT_FOUND}
            )

        queryset = (
            Room.objects.not_participated_by(user)
            .with_participants_count()
            .with_details()
            .ordered_by_popularity()
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
        queryset = Topic.objects.all()

        return TopicFilter(
            data={"search": search, "min_rooms": min_rooms},
            queryset=queryset,
        ).qs.ordered_by_popularity()
