import graphene
from .types import RoomType, TopicType, MessageType, UserType, AuthStatusType
from ..models import Room, Topic, User
from django.db.models import Q, Count
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

class Query(graphene.ObjectType):
    rooms = graphene.List(
        RoomType,
        host_slug=graphene.String(),
        search=graphene.String(),
        topic=graphene.String()
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
        try:
            room = Room.objects.get(
                host__slug=host_slug,
                slug=room_slug
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})
        
        return room

    def resolve_messages(self, info, host_slug, room_slug):
        try:
            room = Room.objects.get(
                host__slug=host_slug,
                slug=room_slug
            )
        except Room.DoesNotExist:
            raise GraphQLError("Room not found", extensions={"code": "NOT_FOUND"})

        return room.message_set.all().order_by('created')

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
            user = User.objects.get(slug=user_slug)
        except User.DoesNotExist:
            raise GraphQLError("User not found", extensions={"code": "NOT_FOUND"})

        return user
