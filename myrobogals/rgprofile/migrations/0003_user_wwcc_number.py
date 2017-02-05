# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgprofile', '0002_remove_memberstatustype_type_of_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='wwcc_number',
            field=models.CharField(default=False, max_length=20),
            preserve_default=True,
        ),
    ]
