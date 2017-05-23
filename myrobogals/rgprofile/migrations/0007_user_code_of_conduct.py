# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rgprofile', '0006_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='code_of_conduct',
            field=models.BooleanField(default=False),
        ),
    ]
