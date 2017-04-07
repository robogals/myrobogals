# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rgconf', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conferenceattendee',
            name='email',
            field=models.EmailField(max_length=254, verbose_name=b'E-mail address'),
        ),
        migrations.AlterField(
            model_name='conferenceattendee',
            name='parts_attending',
            field=models.ManyToManyField(to='rgconf.ConferencePart', blank=True),
        ),
    ]
