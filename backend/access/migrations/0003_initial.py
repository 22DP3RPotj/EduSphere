from django.db import migrations


def create_permissions(apps, schema_editor):
    Permission = apps.get_model("access", "Permission")

    permissions = {
        "room.delete": "Delete room",
        "room.update": "Update room settings",
        "room.manage_visibility": "Manage room visibility settings",
        "room.invite": "Send and manage room invitations",
        "room.kick": "Remove users from the room",
        "room.role_manage": "Manage room roles and permissions",
        "room.delete_message": "Delete messages from the room",
        "room.upload_file": "Allow file uploads",
    }

    for code, description in permissions.items():
        Permission.objects.get_or_create(
            code=code,
            defaults={"description": description},
        )


def remove_permissions(apps, schema_editor):
    Permission = apps.get_model("access", "Permission")

    Permission.objects.filter(
        code__in=[
            "room.delete",
            "room.update",
            "room.manage_visibility",
            "room.invite",
            "room.kick",
            "room.role_manage",
            "room.delete_message",
            "room.upload_file",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("access", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(create_permissions, remove_permissions),
    ]
