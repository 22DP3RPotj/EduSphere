from django.db import migrations


PERMISSIONS = {
    "room.delete": "Delete room",
    "room.update": "Update room settings",
    "room.manage_visibility": "Manage room visibility settings",
    "room.manage_participants": "Invite or remove participants",
    "room.manage_roles": "Manage room roles and permissions",
    "room.delete_message": "Delete messages from the room",
    "room.upload_file": "Allow file uploads",
}


def create_permissions(apps, schema_editor):
    Permission = apps.get_model("access", "Permission")

    for code, description in PERMISSIONS.items():
        Permission.objects.update_or_create(
            code=code,
            defaults={"description": description},
        )


def remove_permissions(apps, schema_editor):
    Permission = apps.get_model("access", "Permission")

    Permission.objects.filter(code__in=PERMISSIONS.keys()).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("access", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(create_permissions, remove_permissions),
    ]
