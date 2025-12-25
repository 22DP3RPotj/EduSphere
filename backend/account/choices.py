from django.db import models


class LanguageChoices(models.TextChoices):
    ENGLISH = "en", "English"
    LATVIAN = "lv", "Latvian"
