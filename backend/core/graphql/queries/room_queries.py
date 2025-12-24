import graphene
from typing import Optional
from graphql import GraphQLError

from django.db.models import Q, Count, QuerySet

from backend.core.graphql.types import RoomType
from backend.core.models import Room, User


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
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        return room

    def resolve_rooms(
        self,
        info: graphene.ResolveInfo,
        host_slug: Optional[str] = None,
        search: Optional[str] = None,
        topics: Optional[list[str]] = None
    ) -> QuerySet[Room]:
        queryset = Room.objects.annotate(
            participants_count=Count('participants')
        ).select_related('host').prefetch_related('topics', 'participants__user', 'participants__role')

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
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        queryset = Room.objects.filter(participants=user).annotate(
            participants_count=Count('participants')
        ).order_by(
            '-participants_count', '-created_at'
        ).select_related('host').prefetch_related('topics', 'participants__user', 'participants__role')

        return queryset
    
    def resolve_rooms_not_participated_by_user(self, info: graphene.ResolveInfo, user_slug: str) -> QuerySet[Room]:
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        queryset = Room.objects.exclude(participants=user).annotate(
            participants_count=Count('participants')
        ).order_by('-participants_count', '-created_at').select_related('host').prefetch_related('topics', 'participants__user', 'participants__role')

        return queryset
    