import django_filters
from django.utils import timezone

from backend.invite.models import Invite
from backend.invite.choices import InviteStatusChoices


class InviteFilter(django_filters.FilterSet):
    # Foreign key lookups
    room = django_filters.UUIDFilter(field_name="room_id")
    inviter = django_filters.UUIDFilter(field_name="inviter_id")
    invitee = django_filters.UUIDFilter(field_name="invitee_id")

    # Status
    status = django_filters.ChoiceFilter(choices=InviteStatusChoices.choices)

    # Date ranges
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    expires_after = django_filters.DateTimeFilter(
        field_name="expires_at", lookup_expr="gte"
    )
    expires_before = django_filters.DateTimeFilter(
        field_name="expires_at", lookup_expr="lte"
    )

    # Computed
    is_expired = django_filters.BooleanFilter(method="filter_is_expired")
    is_active = django_filters.BooleanFilter(method="filter_is_active")

    class Meta:
        model = Invite
        fields: list[str] = []

    def filter_is_expired(self, queryset, name, value):
        """Filter on expires_at directly — avoids relying on status being up to date."""
        now = timezone.now()
        if value:
            return queryset.filter(expires_at__lt=now)
        return queryset.filter(expires_at__gte=now)

    def filter_is_active(self, queryset, name, value):
        """Pending and not expired — mirrors the is_active property on the model."""
        now = timezone.now()
        if value:
            return queryset.filter(
                status=Invite.Status.PENDING,
            ).filter(expires_at__gt=now)
        return queryset.exclude(
            status=Invite.Status.PENDING,
            expires_at__gt=now,
        )
