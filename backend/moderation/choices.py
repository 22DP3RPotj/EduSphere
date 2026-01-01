from django.db import models


class ReportStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    RESOLVED = 'RESOLVED', 'Resolved'
    DISMISSED = 'DISMISSED', 'Dismissed'

class ReportReason(models.TextChoices):
    SPAM = 'SPAM', 'Spam'
    HARASSMENT = 'HARASSMENT', 'Harassment'
    INAPPROPRIATE_CONTENT = 'INAPPROPRIATE_CONTENT', 'Inappropriate Content'
    HATE_SPEECH = 'HATE_SPEECH', 'Hate Speech'
    OTHER = 'OTHER', 'Other'


ACTIVE_STATUSES = (
    ReportStatus.PENDING,
    ReportStatus.UNDER_REVIEW,
)
    