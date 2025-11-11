import graphene
from django.db.models import Count
from backend.core.graphql.types import TopicType
from backend.core.models import Topic


class TopicQuery(graphene.ObjectType):
    topics = graphene.List(
        TopicType,
        search=graphene.String(),
        min_rooms=graphene.Int()
    )
     
    def resolve_topics(self, info, search=None, min_rooms=None):
        queryset = Topic.objects.annotate(
            room_count=Count('rooms')
        )
        
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        if min_rooms:
            queryset = queryset.filter(room_count__gte=min_rooms)

        return queryset.order_by('-room_count')