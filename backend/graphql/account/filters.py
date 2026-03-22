import django_filters
from django.db import models

from backend.account.models import User


class UserFilter(django_filters.FilterSet):
    # Search
    search = django_filters.CharFilter(method="filter_search", label="Search")

    # Boolean flags
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_staff = django_filters.BooleanFilter(field_name="is_staff")
    is_superuser = django_filters.BooleanFilter(field_name="is_superuser")
    has_avatar = django_filters.BooleanFilter(method="filter_has_avatar")
    has_active_ban = django_filters.BooleanFilter(method="filter_has_active_ban")

    # Date ranges
    date_joined_after = django_filters.DateTimeFilter(
        field_name="date_joined", lookup_expr="gte"
    )
    date_joined_before = django_filters.DateTimeFilter(
        field_name="date_joined", lookup_expr="lte"
    )
    last_seen_after = django_filters.DateTimeFilter(
        field_name="last_seen", lookup_expr="gte"
    )
    last_seen_before = django_filters.DateTimeFilter(
        field_name="last_seen", lookup_expr="lte"
    )

    class Meta:
        model = User
        fields: list[str] = []

    def filter_search(self, queryset, name, value):
        """Search across username, name, and email."""
        return queryset.filter(
            models.Q(username__icontains=value)
            | models.Q(name__icontains=value)
            | models.Q(email__icontains=value)
        )

    def filter_has_avatar(self, queryset, name, value):
        """Filter users who have or don't have an avatar set."""
        if value:
            return queryset.exclude(avatar__isnull=True).exclude(avatar="")
        return queryset.filter(models.Q(avatar__isnull=True) | models.Q(avatar=""))

    def filter_has_active_ban(self, queryset, name, value):
        """Filter users who currently have an active ban."""
        if value:
            return queryset.filter(bans__is_active=True).distinct()
        return queryset.exclude(bans__is_active=True).distinct()
