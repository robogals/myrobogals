# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgteaching', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolvisitstats',
            name='notes',
            field=models.TextField(verbose_name=b'General notes', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='schoolvisitstats',
            name='visit_type',
            field=models.IntegerField(choices=[(0, b'Robogals workshop, metro area'), (7, b'Robogals workshop, regional area'), (1, b'Robogals career talk'), (2, b'Robogals event'), (3, b'Non-Robogals workshop'), (4, b'Non-Robogals career talk'), (5, b'Non-Robogals event'), (6, b'Other')]),
            preserve_default=True,
        ),
    ]
