# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rgteaching', '0003_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='date_modified',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='schoolvisit',
            name='created_method',
            field=models.IntegerField(default=0, choices=[(0, b'Event'), (1, b'QuickEntry')]),
        ),
    ]
