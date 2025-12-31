# Generated migration to add room app relations

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0002_initial'),
        ('room', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='room.room'),
        ),
        migrations.AddField(
            model_name='participant',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='room.room'),
        ),
        migrations.AddConstraint(
            model_name='role',
            constraint=models.UniqueConstraint(fields=('room', 'name'), name='unique_role_name_per_room'),
        ),
        migrations.AddIndex(
            model_name='participant',
            index=models.Index(fields=['room', 'joined_at'], name='access_part_room_id_880552_idx'),
        ),
        migrations.AddIndex(
            model_name='participant',
            index=models.Index(fields=['room', 'user'], name='access_part_room_id_341e1a_idx'),
        ),
        migrations.AddIndex(
            model_name='participant',
            index=models.Index(fields=['room', 'role'], name='access_part_room_id_9a1d86_idx'),
        ),
        migrations.AddConstraint(
            model_name='participant',
            constraint=models.UniqueConstraint(fields=('user', 'room'), name='unique_participant'),
        ),
    ]
