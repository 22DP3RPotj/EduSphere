from django.apps import AppConfig


class InviteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.invite"
    label = "invite"
    verbose_name = "Invite Management"
