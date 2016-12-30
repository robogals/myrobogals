# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgprofile', '0001_initial'),
        ('rgchapter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='notify_list',
            field=models.ForeignKey(related_name='chapter_notify_list', verbose_name=b'Who to notify', blank=True, to='rgprofile.UserList', null=True),
            preserve_default=True,
        ),
    ]
