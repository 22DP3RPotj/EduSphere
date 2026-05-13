from django.db import models


class MessageStatusChoices(models.TextChoices):
    DELIVERED = "DELIVERED", "Delivered"
    SEEN = "SEEN", "Seen"
