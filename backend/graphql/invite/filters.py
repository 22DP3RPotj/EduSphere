import django_filters
from django.utils import timezone
from django.db.models import Q

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
        expired_q = Q(expires_at__lt=now)
        return queryset.filter(expired_q) if value else queryset.exclude(expired_q)

    def filter_is_active(self, queryset, name, value):
        """Pending and not expired — mirrors the is_active property on the model."""
        now = timezone.now()
        active_q = Q(status=Invite.Status.PENDING) & (
            Q(expires_at__isnull=True) | Q(expires_at__gte=now)
        )
        return queryset.filter(active_q) if value else queryset.exclude(active_q)
