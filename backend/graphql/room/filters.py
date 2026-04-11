import django_filters
from django.db.models import Q

from backend.room.models import Room, Topic


class RoomFilter(django_filters.FilterSet):
    host_id = django_filters.UUIDFilter(field_name="host__id", lookup_expr="exact")
    host_slug = django_filters.CharFilter(
        field_name="host__username", lookup_expr="exact"
    )
    search = django_filters.CharFilter(method="filter_search")
    topics = django_filters.ModelMultipleChoiceFilter(
        field_name="topics__name",
        to_field_name="name",
        queryset=lambda _: Topic.objects.all(),
    )

    class Meta:
        model = Room
        fields: list[str] = []

    def filter_search(self, queryset, name, value):
        """Search across name and description."""
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )


class TopicFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    min_rooms = django_filters.NumberFilter(method="filter_min_rooms")

    class Meta:
        model = Topic
        fields: list[str] = []

    def filter_min_rooms(self, queryset, name, value):
        """Filter topics with a minimum number of associated rooms."""
        return queryset.with_rooms_count().filter(room_count__gte=value)
