from django.db import models


class VisibilityChoices(models.TextChoices):
    PUBLIC = "PUBLIC", "Public"
    PRIVATE = "PRIVATE", "Private"
