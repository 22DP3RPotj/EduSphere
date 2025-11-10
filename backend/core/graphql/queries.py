import graphene
from django.db.models import Q, Count
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from .types import RoomType, TopicType, MessageType, UserType, AuthStatusType
from ..models import Room, Topic, User

class Query(graphene.ObjectType):
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
    room = graphene.Field(
        RoomType,
        host_slug=graphene.String(required=True),
        room_slug=graphene.String(required=True)
    )
    topics = graphene.List(
        TopicType,
        search=graphene.String(),
        min_rooms=graphene.Int()
    )
    messages = graphene.List(
        MessageType,
        host_slug=graphene.String(required=True),
        room_slug=graphene.String(required=True)
    )
    messages_by_user = graphene.List(
        MessageType,
        user_slug=graphene.String(required=True),   
    )
    users = graphene.List(
        UserType,
        search=graphene.String()
    )
    user = graphene.Field(
        UserType,
        user_slug=graphene.String(required=True),
    )
    
    auth_status = graphene.Field(AuthStatusType)
    me = graphene.Field(UserType)
    
    @login_required
    def resolve_me(self, info):
        return info.context.user
    
    def resolve_auth_status(self, info):
        user = info.context.user
        if user.is_authenticated:
            return AuthStatusType(is_authenticated=True, user=user)
        return AuthStatusType(is_authenticated=False, user=None)


    def resolve_rooms(self, info, host_slug=None, search=None, topics=None):
        queryset = Room.objects.annotate(
            participants_count=Count('participants')
        ).select_related('host').prefetch_related('topics')

        if host_slug:
            queryset = queryset.filter(host__username=host_slug)
            
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            
        if topics:
            queryset = queryset.filter(topics__name__in=topics).distinct()

        return queryset.order_by('-participants_count' , '-created')
    
    def resolve_rooms_participated_by_user(self, info, user_slug):
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        queryset = Room.objects.filter(participants=user).annotate(
            participants_count=Count('participants')
        ).order_by('-participants_count', '-created')

        return queryset
    
    def resolve_rooms_not_participated_by_user(self, info, user_slug):
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        queryset = Room.objects.exclude(participants=user).annotate(
            participants_count=Count('participants')
        ).order_by('-participants_count', '-created')

        return queryset

    def resolve_topics(self, info, search=None, min_rooms=None):
        queryset = Topic.objects.annotate(
            room_count=Count('rooms')
        )
        
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        if min_rooms:
            queryset = queryset.filter(room_count__gte=min_rooms)

        return queryset.order_by('-room_count')

    def resolve_room(self, info, host_slug, room_slug):
        try:
            room = Room.objects.get(
                host__username=host_slug,
                slug=room_slug
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        return room

    def resolve_messages(self, info, host_slug, room_slug):
        try:
            room = Room.objects.get(
                host__username=host_slug,
                slug=room_slug
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})

        return room.message_set.all().order_by('created')
    
    def resolve_messages_by_user(self, info, user_slug):
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        return user.message_set.all().order_by('-created')
    

    def resolve_users(self, info, search=None):
        queryset = User.objects.all().prefetch_related('hosted_rooms')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(name__icontains=search)
            )
        return queryset
    
    def resolve_user(self, info, user_slug):
        try:
            user = User.objects.get(username=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        return user
