from django.db import models

class MessageStatusChoices(models.TextChoices):
    SENT = 'SENT', 'Sent'
    DELIVERED = 'DELIVERED', 'Delivered'
    SEEN = 'SEEN', 'Seen'