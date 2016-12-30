# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgchapter', '0002_chapter_notify_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site_name', models.CharField(max_length=64)),
                ('site_url', models.CharField(max_length=64)),
                ('ftp_host', models.CharField(max_length=64, blank=True)),
                ('ftp_user', models.CharField(max_length=64, blank=True)),
                ('ftp_pass', models.CharField(max_length=64, blank=True)),
                ('ftp_path', models.CharField(max_length=64, blank=True)),
                ('sql_host_int', models.CharField(max_length=64, blank=True)),
                ('sql_host_ext', models.CharField(max_length=64, blank=True)),
                ('sql_user', models.CharField(max_length=64, blank=True)),
                ('sql_pass', models.CharField(max_length=64, blank=True)),
                ('sql_dbname', models.CharField(max_length=64, blank=True)),
                ('joomla_admin_url', models.CharField(max_length=64, blank=True)),
                ('joomla_user', models.CharField(max_length=64, blank=True)),
                ('joomla_pass', models.CharField(max_length=64, blank=True)),
                ('site_chapter', models.ForeignKey(to='rgchapter.Chapter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
