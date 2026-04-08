from django.db import models


class LanguageChoices(models.TextChoices):
    ENGLISH = "en", "English"
    LATVIAN = "lv", "Latvian"


class UserStatusChoices(models.TextChoices):
    PUBLIC = "public", "Public"
    PRIVATE = "private", "Private"
    ARCHIVED = "archived", "Archived"
    TERMINATED = "terminated", "Terminated"


class EmailTypeChoices(models.TextChoices):
    VERIFICATION = "verification", "Verification"
    PASSWORD_RESET = "password_reset", "Password Reset"
