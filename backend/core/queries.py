import graphene
from .types import RoomType, TopicType, MessageType, UserType
from .models import Room, Topic, User
from django.db.models import Q, Count
from graphql_jwt.decorators import login_required
from django.shortcuts import get_object_or_404

class Query(graphene.ObjectType):
    rooms = graphene.List(
        RoomType,
        host_slug=graphene.String(),
        search=graphene.String(),
        topic=graphene.String()
    )
    topics = graphene.List(
        TopicType,
        search=graphene.String(),
        min_rooms=graphene.Int()
    )
    room = graphene.Field(
        RoomType,
        host_slug=graphene.String(required=True),
        room_slug=graphene.String(required=True)
    )
    messages = graphene.List(
        MessageType,
        host_slug=graphene.String(required=True),
        room_slug=graphene.String(required=True)
    )
    
    # User-related queries
    me = graphene.Field(UserType)
    users = graphene.List(UserType, search=graphene.String())

    @login_required
    def resolve_me(self, info):
        return info.context.user

    def resolve_rooms(self, info, host_slug=None, search=None, topic=None):
        queryset = Room.objects.annotate(
            participants_count=Count('participants')
        ).select_related('host', 'topic')

        if host_slug:
            queryset = queryset.filter(host__slug=host_slug)
            
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            
        if topic:
            queryset = queryset.filter(topic__name__iexact=topic)

        return queryset.order_by('-created')

    def resolve_topics(self, info, search=None, min_rooms=None):
        queryset = Topic.objects.annotate(
            room_count=Count('room')
        )
        
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        if min_rooms:
            queryset = queryset.filter(room_count__gte=min_rooms)

        return queryset.order_by('-room_count')

    def resolve_room(self, info, host_slug, room_slug):
        return get_object_or_404(
            Room,
            host__slug=host_slug,
            slug=room_slug
        )

    def resolve_messages(self, info, host_slug, room_slug):
        room = get_object_or_404(
            Room,
            host__slug=host_slug,
            slug=room_slug
        )
        return room.message_set.all().order_by('created')

    def resolve_users(self, info, search=None):
        queryset = User.objects.all().prefetch_related('hosted_rooms')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(name__icontains=search)
            )
        return queryset