# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rgmessages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailmessage',
            name='from_address',
            field=models.EmailField(max_length=254, verbose_name=b'From Address'),
        ),
        migrations.AlterField(
            model_name='emailrecipient',
            name='to_address',
            field=models.EmailField(max_length=254, verbose_name=b'To Email'),
        ),
        migrations.AlterField(
            model_name='newslettersubscriber',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
