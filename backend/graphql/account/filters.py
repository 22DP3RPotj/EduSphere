import django_filters
from django.db import models

from backend.account.models import User


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Search")

    class Meta:
        model = User
        fields = ["search"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(username__icontains=value) | models.Q(name__icontains=value)
        )
