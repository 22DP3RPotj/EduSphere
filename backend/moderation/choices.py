from django.db import models


class CaseStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    RESOLVED = "RESOLVED", "Resolved"
    DISMISSED = "DISMISSED", "Dismissed"

    @classmethod
    def active(cls) -> tuple[str, ...]:
        return (cls.PENDING, cls.UNDER_REVIEW)

    @classmethod
    def finalized(cls) -> tuple[str, ...]:
        return (cls.RESOLVED, cls.DISMISSED)


class ActionChoices(models.TextChoices):
    NO_VIOLATION = "NO_VIOLATION", "No Violation"
    CONTENT_REMOVED = "CONTENT_REMOVED", "Content Removed"
    WARNING = "WARNING", "Warning"
    TEMP_BAN = "TEMP_BAN", "Temporary Ban"
    PERM_BAN = "PERM_BAN", "Permanent Ban"


class ActionPriorityChoices(models.IntegerChoices):
    LOW = 0, "Low"
    MEDIUM = 1, "Medium"
    HIGH = 2, "High"
