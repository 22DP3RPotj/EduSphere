from django.apps import AppConfig


class RoomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.room"
    label = "room"
    verbose_name = "Room Management"
