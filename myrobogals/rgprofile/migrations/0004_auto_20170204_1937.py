# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgprofile', '0003_user_wwcc_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='wwcc_expiration',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='wwcc_number',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
    ]
