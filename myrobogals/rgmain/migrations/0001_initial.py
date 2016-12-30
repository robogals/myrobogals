# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, verbose_name=b'ISO 3166-1 code', primary_key=True)),
                ('country_name', models.CharField(max_length=128, verbose_name=b'Country')),
            ],
            options={
                'ordering': ('country_name', 'code'),
                'verbose_name_plural': 'countries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MobileRegex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('regex', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=64)),
                ('strip_digits', models.SmallIntegerField(default=0)),
                ('prepend_digits', models.CharField(max_length=16, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Mobile regexes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MobileRegexCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=64)),
                ('errmsg', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subdivision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=3, verbose_name=b'ISO 3166-2 code')),
                ('subdivision_name', models.CharField(max_length=128, verbose_name=b'Name')),
                ('country', models.ForeignKey(to='rgmain.Country')),
            ],
            options={
                'ordering': ('subdivision_name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Timezone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'university',
                'verbose_name_plural': 'universities',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mobileregex',
            name='collection',
            field=models.ForeignKey(to='rgmain.MobileRegexCollection'),
            preserve_default=True,
        ),
    ]
