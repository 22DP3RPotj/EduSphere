import django_filters
from backend.account.models import UserBanHistory, UserHistory, User
from backend.moderation.models import (
    ModerationActionHistory,
    ModerationCaseHistory,
    ReportHistory,
)
from backend.room.models import RoomHistory
from backend.invite.models import InviteHistory, InviteLinkHistory


class BaseAuditFilter(django_filters.FilterSet):
    # Pghistory event metadata filters
    date_from = django_filters.DateFilter(
        field_name="pgh_created_at", lookup_expr="date__gte"
    )
    date_to = django_filters.DateFilter(
        field_name="pgh_created_at", lookup_expr="date__lte"
    )
    event_label = django_filters.CharFilter(field_name="pgh_label", lookup_expr="exact")
    target_id = django_filters.UUIDFilter(field_name="pgh_obj_id")

    # Actor filter (filters events by the user who performed the action)
    actor = django_filters.UUIDFilter(method="filter_actor")
    actor_username = django_filters.CharFilter(method="filter_actor_username")

    def filter_actor(self, queryset, name, value):
        return queryset.filter(pgh_context__metadata__user=str(value))

    def filter_actor_username(self, queryset, name, value):
        user_id = (
            User.objects.filter(username__iexact=value)
            .values_list("id", flat=True)
            .first()
        )

        if not user_id:
            return queryset.none()

        return queryset.filter(pgh_context__metadata__user=str(user_id))


class UserAuditFilter(BaseAuditFilter):
    class Meta:
        model = UserHistory
        fields = ["is_staff", "is_superuser", "is_active"]


class UserBanAuditFilter(BaseAuditFilter):
    class Meta:
        model = UserBanHistory
        fields = ["is_active"]


class RoomAuditFilter(BaseAuditFilter):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = RoomHistory
        fields = ["name", "visibility"]


class InviteAuditFilter(BaseAuditFilter):
    class Meta:
        model = InviteHistory
        fields = ["status"]


class InviteLinkAuditFilter(BaseAuditFilter):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = InviteLinkHistory
        fields = ["is_active"]


class ReportAuditFilter(BaseAuditFilter):
    class Meta:
        model = ReportHistory
        fields = ["case__status", "case__priority"]


class ModerationCaseAuditFilter(BaseAuditFilter):
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    priority = django_filters.CharFilter(field_name="priority", lookup_expr="exact")

    class Meta:
        model = ModerationCaseHistory
        fields = ["status", "priority"]


class ModerationActionAuditFilter(BaseAuditFilter):
    action = django_filters.CharFilter(field_name="action", lookup_expr="exact")

    class Meta:
        model = ModerationActionHistory
        fields = ["action"]
