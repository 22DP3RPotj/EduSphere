from django.db import models


class ReportStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    RESOLVED = "RESOLVED", "Resolved"
    DISMISSED = "DISMISSED", "Dismissed"


ACTIVE_STATUSES = (
    ReportStatus.PENDING,
    ReportStatus.UNDER_REVIEW,
)
