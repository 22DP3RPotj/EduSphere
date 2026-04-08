from django.db import models


class LanguageChoices(models.TextChoices):
    ENGLISH = "en", "English"
    LATVIAN = "lv", "Latvian"


class UserStatusChoices(models.TextChoices):
    PUBLIC = "public", "Public"
    PRIVATE = "private", "Private"
    ARCHIVED = "archived", "Archived"
    TERMINATED = "terminated", "Terminated"
