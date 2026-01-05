from django.apps import AppConfig


class InfraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.infra"
    label = "infra"
    verbose_name = "Infrastructure"
