from django.apps import AppConfig


class ModerationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.moderation"
    label = "moderation"
    verbose_name = "Moderation"

    def ready(self):
        import backend.moderation.rules.permissions as _  # noqa
