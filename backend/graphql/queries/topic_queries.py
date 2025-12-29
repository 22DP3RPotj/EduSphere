import graphene
from typing import Optional

from django.db.models import Count, QuerySet

from backend.graphql.types import TopicType
from backend.core.models import Topic


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