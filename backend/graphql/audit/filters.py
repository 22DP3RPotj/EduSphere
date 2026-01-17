import django_filters


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
        fields = ["username", "email", "is_staff", "is_superuser", "is_active"]


class RoomAuditFilter(BaseAuditFilter):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        fields = ["name", "visibility"]


class InviteAuditFilter(BaseAuditFilter):
    class Meta:
        fields = ["status"]
