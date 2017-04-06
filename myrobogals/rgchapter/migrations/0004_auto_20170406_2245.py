# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgchapter', '0003_auto_20170107_0341'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='police_check_number_enable',
            field=models.BooleanField(default=False, verbose_name=b'Enable police check number field'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chapter',
            name='police_check_number_label',
            field=models.CharField(max_length=64, verbose_name=b'Label for police check number field', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chapter',
            name='police_check_number_required',
            field=models.BooleanField(default=False, verbose_name=b'Require student police check number field to be filled'),
            preserve_default=True,
        ),
    ]
