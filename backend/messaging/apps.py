from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.messaging"
    label = "messaging"
    verbose_name = "Messaging"
