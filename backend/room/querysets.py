from django.db import models
from typing import Self
from backend.access.models import Participant
from backend.account.models import User


class RoomQuerySet(models.QuerySet):
    """Custom QuerySet for Room model."""

    def public(self):
        return self.filter(visibility=self.model.Visibility.PUBLIC)

    def private(self):
        return self.filter(visibility=self.model.Visibility.PRIVATE)

    def visible_to(self, user: User) -> Self:
        """Filter rooms visible to a specific user."""
        filters = models.Q(visibility=self.model.Visibility.PUBLIC)

        if user.is_authenticated:
            filters |= models.Q(memberships__user=user)

        return self.filter(filters).distinct()

    def participated_by(self, user: User) -> Self:
        """Filter rooms participated by a specific user."""
        return self.filter(memberships__user=user)

    def not_participated_by(self, user: User) -> Self:
        """Filter rooms not participated by a specific user."""
        return self.exclude(memberships__user=user)

    def with_host(self) -> Self:
        """Optimize query by selecting related host."""
        return self.select_related("host")

    def with_topic(self) -> Self:
        """Optimize query by prefetching related topics."""
        return self.prefetch_related("topics")

    def with_memberships(self) -> Self:
        """Prefetch memberships with user and role details."""
        return self.prefetch_related(
            models.Prefetch(
                "memberships",
                queryset=Participant.objects.select_related("user", "role"),
            ),
        )

    def with_details(self) -> Self:
        """Optimize query by selecting related host and prefetching topics and memberships."""
        return self.with_host().with_topic().with_memberships()

    def ordered_by_popularity(self) -> Self:
        """Order rooms by number of participants and creation date."""
        return self.order_by("-participants_count", "-created_at")

    def with_participants_count(self) -> Self:
        """Annotate rooms with the count of participants."""
        return self.annotate(
            participants_count=models.Count("participants", distinct=True)
        )


class TopicQuerySet(models.QuerySet):
    """Custom QuerySet for Topic model."""

    def with_rooms_count(self) -> Self:
        """Annotate topics with the count of associated rooms."""
        return self.annotate(room_count=models.Count("rooms"))

    def ordered_by_popularity(self) -> Self:
        """Order topics by number of associated rooms and name."""
        return self.with_rooms_count().order_by("-room_count", "name")
