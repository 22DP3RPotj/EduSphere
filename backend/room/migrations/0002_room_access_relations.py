# Generated migration to add access app relations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0001_initial'),
        ('access', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='default_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='default_for_rooms', to='access.role'),
        ),
        migrations.AddField(
            model_name='room',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='participants', through='access.Participant', to=settings.AUTH_USER_MODEL),
        ),
    ]
