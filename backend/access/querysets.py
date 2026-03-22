from django.db import models
from typing import Self, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.room.models import Room


class RoleQuerySet(models.QuerySet):
    """Custom QuerySet for access-related models, providing common filtering methods."""

    def with_permissions(self) -> Self:
        """Optimize query by prefetching related permissions."""
        return self.prefetch_related("permissions")

    def with_room(self) -> Self:
        """Optimize query by selecting related room."""
        return self.select_related("room")

    def by_room(self, room: "Room") -> Self:
        """Filter queryset by room ID."""
        return self.filter(room=room)
