from typing import Optional
import django_filters

from django.contrib.contenttypes.models import ContentType

from backend.moderation.models import Report, ModerationCase
from backend.moderation.choices import CaseStatusChoices, ActionPriorityChoices
from backend.graphql.moderation.types import ReportTargetTypeEnum


def _get_content_type_for_target(target_type: str) -> Optional[ContentType]:
    from backend.room.models import Room
    from backend.account.models import User
    from backend.messaging.models import Message

    model_map = {
        ReportTargetTypeEnum.ROOM: Room,
        ReportTargetTypeEnum.USER: User,
        ReportTargetTypeEnum.MESSAGE: Message,
    }
    model = model_map.get(target_type)
    if model is None:
        return None
    return ContentType.objects.get_for_model(model)


class ReportFilter(django_filters.FilterSet):
    # Foreign key lookups
    reason = django_filters.UUIDFilter(field_name="reason_id")
    reporter = django_filters.UUIDFilter(field_name="reporter_id")
    case = django_filters.UUIDFilter(field_name="case_id")

    # Computed
    has_case = django_filters.BooleanFilter(method="filter_has_case")
    target_type = django_filters.CharFilter(method="filter_target_type")

    # Date ranges
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Report
        fields: list[str] = []

    def filter_has_case(self, queryset, name, value):
        """Filter reports that have or haven't been assigned to a moderation case."""
        if value:
            return queryset.filter(case__isnull=False)
        return queryset.filter(case__isnull=True)

    def filter_target_type(self, queryset, name, value):
        """Filter reports by target content type (room, user, message)."""
        ct = _get_content_type_for_target(value)
        if ct is None:
            return queryset.none()
        return queryset.filter(content_type=ct)


class ModerationCaseFilter(django_filters.FilterSet):
    # Enum filters
    status = django_filters.ChoiceFilter(choices=CaseStatusChoices.choices)
    priority = django_filters.ChoiceFilter(choices=ActionPriorityChoices.choices)

    # Computed
    has_actions = django_filters.BooleanFilter(method="filter_has_actions")
    target_type = django_filters.CharFilter(method="filter_target_type")

    # Date ranges
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    updated_after = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte"
    )
    updated_before = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte"
    )

    class Meta:
        model = ModerationCase
        fields: list[str] = []

    def filter_has_actions(self, queryset, name, value):
        """Filter cases that have or haven't had any moderation actions taken."""
        if value:
            return queryset.filter(actions__isnull=False).distinct()
        return queryset.filter(actions__isnull=True)

    def filter_target_type(self, queryset, name, value):
        """Filter cases by target content type (room, user, message)."""
        ct = _get_content_type_for_target(value)
        if ct is None:
            return queryset.none()
        return queryset.filter(content_type=ct)
