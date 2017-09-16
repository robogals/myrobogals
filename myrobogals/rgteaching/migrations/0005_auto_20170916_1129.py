# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rgteaching', '0004_auto_20170512_2126'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='privacy',
            field=models.IntegerField(default=0, choices=[(0, b'Private'), (1, b'Public')]),
        ),
        migrations.AlterField(
            model_name='schoolvisit',
            name='created_method',
            field=models.IntegerField(default=0, choices=[(0, b'Event'), (1, b'QuickEntry'), (2, b'Import')]),
        ),
    ]
