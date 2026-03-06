from django.db import migrations
from django.utils.text import slugify

REASONS_ALL = ["Spam", "Harassment", "Inappropriate Content", "Hate Speech", "Other"]
REASONS_USER_ONLY = ["Impersonation"]
REASONS_ROOM_ONLY = ["Off-topic Content"]


def create_reasons(apps, schema_editor):
    ReportReason = apps.get_model("moderation", "ReportReason")
    ContentType = apps.get_model("contenttypes", "ContentType")

    user_ct, _ = ContentType.objects.get_or_create(app_label="account", model="user")
    room_ct, _ = ContentType.objects.get_or_create(app_label="room", model="room")

    for label in REASONS_ALL:
        ReportReason.objects.update_or_create(slug=slugify(label), defaults={"label": label, "is_active": True})

    for label in REASONS_USER_ONLY:
        reason, _ = ReportReason.objects.update_or_create(slug=slugify(label), defaults={"label": label, "is_active": True})
        reason.allowed_content_types.set([user_ct])

    for label in REASONS_ROOM_ONLY:
        reason, _ = ReportReason.objects.update_or_create(slug=slugify(label), defaults={"label": label, "is_active": True})
        reason.allowed_content_types.set([room_ct])


def remove_reasons(apps, schema_editor):
    ReportReason = apps.get_model("moderation", "ReportReason")
    all_labels = REASONS_ALL + REASONS_USER_ONLY + REASONS_ROOM_ONLY
    slugs = [slugify(label) for label in all_labels]
    ReportReason.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('moderation', '0001_initial'),
        ('account', '0001_initial'),
        ('room', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_reasons, remove_reasons),
    ]
