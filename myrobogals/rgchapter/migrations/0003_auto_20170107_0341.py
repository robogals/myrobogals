# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgchapter', '0002_chapter_notify_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='country',
            field=models.ForeignKey(default=b'AU', verbose_name=b'Country', to='rgmain.Country'),
            preserve_default=True,
        ),
    ]
