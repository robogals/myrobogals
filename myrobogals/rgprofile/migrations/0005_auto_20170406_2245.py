# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgprofile', '0004_auto_20170204_1937'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='wwcc_expiration',
            new_name='police_check_expiration',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='wwcc_number',
            new_name='police_check_number',
        ),
    ]
