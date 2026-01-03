import django_filters
from django.db.models import Q

from backend.room.models import Room, Topic


class RoomFilter(django_filters.FilterSet):
    host_slug = django_filters.CharFilter(
        field_name="host__username",
        lookup_expr="exact"
    )
    search = django_filters.CharFilter(
        method="filter_search"
    )
    topics = django_filters.ModelMultipleChoiceFilter(
        field_name="topics__name",
        to_field_name="name",
        queryset=lambda: Topic.objects.all()
    )
    
    class Meta:
        model = Room
        fields: list[str] = []
    
    def filter_search(self, queryset, name, value):
        """Search across name and description."""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )