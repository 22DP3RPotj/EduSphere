from django.apps import AppConfig


class AccessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.access"
    label = "access"
    verbose_name = "Access Control"

    def ready(self):
        import backend.access.rules.permissions as _  # noqa
