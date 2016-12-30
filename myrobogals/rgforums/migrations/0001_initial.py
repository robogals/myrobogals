# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rgchapter', '0002_chapter_notify_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name=b'Name')),
                ('exec_only', models.BooleanField(default=False, verbose_name=b'For executives only')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('chapter', models.ForeignKey(blank=True, to='rgchapter.Chapter', null=True)),
            ],
            options={
                'ordering': ['created_on'],
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name=b'Name')),
                ('description', models.TextField(default=b'')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_post_time', models.DateTimeField(null=True, blank=True)),
                ('blacklist', models.ManyToManyField(related_name='forum_blacklist', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(to='rgforums.Category')),
                ('created_by', models.ForeignKey(related_name='forum_created_by', to=settings.AUTH_USER_MODEL)),
                ('last_post_user', models.ForeignKey(related_name='forum_last_post_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('watchers', models.ManyToManyField(related_name='forum_watchers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_on'],
                'verbose_name': 'forum',
                'verbose_name_plural': 'forums',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ForumSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=255, verbose_name=b'key')),
                ('value', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['key'],
                'verbose_name': 'setting',
                'verbose_name_plural': 'settings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Offense',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes', models.TextField()),
                ('forum', models.ForeignKey(to='rgforums.Forum')),
                ('officer', models.ForeignKey(related_name='offense_officer', to=settings.AUTH_USER_MODEL)),
                ('perpetrator', models.ForeignKey(related_name='offense_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['perpetrator'],
                'verbose_name': 'Offense',
                'verbose_name_plural': 'offenses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(null=True, blank=True)),
                ('edited_by', models.ForeignKey(related_name='post_edited_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('posted_by', models.ForeignKey(related_name='post_posted_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('postfile', models.FileField(upload_to=b'forum_uploads')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=80)),
                ('num_views', models.IntegerField(default=0, verbose_name=b'Number of views')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_post_time', models.DateTimeField(null=True, blank=True)),
                ('sticky', models.BooleanField(default=False, verbose_name=b'Set sticky')),
                ('forum', models.ForeignKey(to='rgforums.Forum')),
                ('last_post_user', models.ForeignKey(related_name='topic_last_post_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('posted_by', models.ForeignKey(related_name='topic_posted_by', to=settings.AUTH_USER_MODEL)),
                ('watchers', models.ManyToManyField(related_name='topic_watchers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-sticky', '-last_post_time'],
                'verbose_name': 'topic',
                'verbose_name_plural': 'topics',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('topic', models.ForeignKey(to='rgforums.Topic')),
                ('voter', models.ForeignKey(related_name='vote', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(to='rgforums.Topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='upload_files',
            field=models.ManyToManyField(related_name='post_upload_files', to='rgforums.PostFile'),
            preserve_default=True,
        ),
    ]
