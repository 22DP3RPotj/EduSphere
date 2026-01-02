from typing import Optional
import graphene
from graphql import GraphQLError

from django.db.models import Q, Count, QuerySet, Prefetch

from backend.access.models import Participant
from backend.core.exceptions import ErrorCode
from backend.account.models import User
from backend.room.models import Room, Topic
from backend.graphql.room.types import RoomType, TopicType


class RoomQuery(graphene.ObjectType):
    room = graphene.Field(
        RoomType,
        host_slug=graphene.String(required=True),
        room_slug=graphene.String(required=True)
    )
    rooms = graphene.List(
        RoomType,
        host_slug=graphene.String(),
        search=graphene.String(),
        topics=graphene.List(graphene.String)
    )
    rooms_participated_by_user = graphene.List(
        RoomType,
        user_slug=graphene.String(required=True)
    )
    rooms_not_participated_by_user = graphene.List(
        RoomType,
        user_slug=graphene.String(required=True)
    )
    
    def resolve_room(self, info: graphene.ResolveInfo, host_slug: str, room_slug: str) -> Room:
        try:
            room = Room.objects.get(
                host__username=host_slug,
                slug=room_slug
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": ErrorCode.NOT_FOUND})
        
        return room

    def resolve_rooms(
        self,
        info: graphene.ResolveInfo,
        host_slug: Optional[str] = None,
        search: Optional[str] = None,
        topics: Optional[list[str]] = None
    ) -> QuerySet[Room]:
        queryset = (
            Room.objects
            .annotate(participants_count=Count('participants'))
            .select_related('host')
            .prefetch_related(
                'topics',
                Prefetch(
                    'memberships',
                    queryset=Participant.objects.select_related('user', 'role')
                )
            )
        )

        if host_slug:
            queryset = queryset.filter(host__username=host_slug)
            
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            
        if topics:
            queryset = queryset.filter(topics__name__in=topics).distinct()

        return queryset.order_by('-participants_count' , '-created_at')
    
    def resolve_rooms_participated_by_user(self, info: graphene.ResolveInfo, user_slug: str) -> QuerySet[Room]:
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": ErrorCode.NOT_FOUND})

        queryset = (
            Room.objects
            .filter(participants=user)
            .annotate(participants_count=Count('participants'))
            .order_by('-participants_count', '-created_at')
            .select_related('host')
            .prefetch_related(
                'topics',
                Prefetch(
                    'memberships',
                    queryset=Participant.objects.select_related('user', 'role')
                )
            )
        )
        
        return queryset
    
    def resolve_rooms_not_participated_by_user(self, info: graphene.ResolveInfo, user_slug: str) -> QuerySet[Room]:
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": ErrorCode.NOT_FOUND})

        queryset = (
            Room.objects
            .exclude(participants=user)
            .annotate(participants_count=Count('participants'))
            .order_by('-participants_count', '-created_at')
            .select_related('host')
            .prefetch_related('topics',
                Prefetch(
                    'memberships',
                    queryset=Participant.objects.select_related('user', 'role')
                )
            )
        )

        return queryset

class TopicQuery(graphene.ObjectType):
    topics = graphene.List(
        TopicType,
        search=graphene.String(),
        min_rooms=graphene.Int()
    )
     
    def resolve_topics(
        self,
        info: graphene.ResolveInfo,
        search: Optional[str] = None,
        min_rooms: Optional[int] = None
    ) -> QuerySet[Topic]:
        queryset = Topic.objects.annotate(
            room_count=Count('rooms')
        )
        
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        if min_rooms:
            queryset = queryset.filter(room_count__gte=min_rooms)

        return queryset.order_by('-room_count')