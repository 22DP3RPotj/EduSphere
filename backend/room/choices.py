from django.db import models


class Visibility(models.TextChoices):
    PUBLIC = 'PUBLIC', 'Public'
    PRIVATE = 'PRIVATE', 'Private'