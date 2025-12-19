from django.db import migrations


def create_permissions(apps, schema_editor):
    Permission = apps.get_model("core", "Permission")

    permissions = [
        "room.delete",
        "room.update",
        "room.manage_visibility",
        "room.invite",
        "room.kick",
        "room.role_manage",
        "room.delete_message",
    ]

    for code in permissions:
        Permission.objects.get_or_create(code=code)


def delete_permissions(apps, schema_editor):
    Permission = apps.get_model("core", "Permission")

    permissions = [
        "room.delete",
        "room.update",
        "room.manage_visibility",
        "room.invite",
        "room.kick",
        "room.role_manage",
        "room.delete_message",
    ]

    Permission.objects.filter(code__in=permissions).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_permissions, delete_permissions),
    ]
