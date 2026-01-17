import django_filters
from backend.account.models import UserHistory
from backend.room.models import RoomHistory
from backend.invite.models import InviteHistory


class BaseAuditFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name="pgh_created_at", lookup_expr="date__gte"
    )
    date_to = django_filters.DateFilter(
        field_name="pgh_created_at", lookup_expr="date__lte"
    )
    action = django_filters.CharFilter(field_name="pgh_label", lookup_expr="exact")
    target_id = django_filters.UUIDFilter(field_name="pgh_obj_id")


class UserAuditFilter(BaseAuditFilter):
    username = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = UserHistory
        fields = ["username", "email", "is_staff", "is_superuser", "is_active"]


class RoomAuditFilter(BaseAuditFilter):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = RoomHistory
        fields = ["name", "visibility"]


class InviteAuditFilter(BaseAuditFilter):
    class Meta:
        model = InviteHistory
        fields = ["status"]
