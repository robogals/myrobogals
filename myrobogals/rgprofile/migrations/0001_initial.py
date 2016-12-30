# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('rgchapter', '0001_initial'),
        ('rgmain', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('alt_email', models.EmailField(max_length=75, verbose_name=b'Alternate e-mail address', blank=True)),
                ('dob', models.DateField(null=True, blank=True)),
                ('dob_public', models.BooleanField(default=False, verbose_name=b'Display date of birth in profile')),
                ('email_public', models.BooleanField(default=False, verbose_name=b'Display email address in profile')),
                ('course', models.CharField(max_length=64, verbose_name=b'Course', blank=True)),
                ('uni_start', models.DateField(null=True, blank=True)),
                ('uni_end', models.DateField(null=True, blank=True)),
                ('job_title', models.CharField(max_length=128, verbose_name=b'Job title', blank=True)),
                ('company', models.CharField(max_length=128, verbose_name=b'Company', blank=True)),
                ('mobile', models.CharField(max_length=16, verbose_name=b'Mobile', blank=True)),
                ('mobile_verified', models.BooleanField(default=False)),
                ('email_reminder_optin', models.BooleanField(default=True, verbose_name=b'Allow email reminders')),
                ('email_chapter_optin', models.BooleanField(default=True, verbose_name=b'Allow emails from chapter')),
                ('mobile_reminder_optin', models.BooleanField(default=True, verbose_name=b'Allow mobile reminders')),
                ('mobile_marketing_optin', models.BooleanField(default=False, verbose_name=b'Allow mobile marketing')),
                ('email_newsletter_optin', models.BooleanField(default=True, verbose_name=b'Subscribe to The Amplifier')),
                ('email_othernewsletter_optin', models.BooleanField(default=True, help_text=b'Ignored unless this user is actually alumni.  It is recommended that you leave this ticked so that the user will automatically be subscribed upon becoming alumni.', verbose_name=b'Subscribe to alumni newsletter (if alumni)')),
                ('photo', models.FileField(upload_to=b'profilepics', blank=True)),
                ('bio', models.TextField(blank=True)),
                ('internal_notes', models.TextField(blank=True)),
                ('website', models.CharField(max_length=200, verbose_name=b'Personal website', blank=True)),
                ('gender', models.IntegerField(default=0, verbose_name=b'Gender', choices=[(0, b'---'), (1, b'Male'), (2, b'Female'), (3, b'Other')])),
                ('privacy', models.IntegerField(default=5, verbose_name=b'Profile privacy', choices=[(20, b'Public'), (10, b'Only Robogals members can see'), (5, b'Only Robogals members in my chapter can see'), (0, b'Private (only committee can see)')])),
                ('course_type', models.IntegerField(default=0, verbose_name=b'Course level', choices=[(0, b'No answer'), (1, b'Undergraduate'), (2, b'Postgraduate')])),
                ('student_type', models.IntegerField(default=0, verbose_name=b'Student type', choices=[(0, b'No answer'), (1, b'Local'), (2, b'International')])),
                ('student_number', models.CharField(max_length=32, verbose_name=b'Student number', blank=True)),
                ('union_member', models.BooleanField(default=False)),
                ('trained', models.BooleanField(default=False)),
                ('security_check', models.BooleanField(default=False)),
                ('name_display', models.IntegerField(blank=True, null=True, verbose_name=b"Override chapter's name display", choices=[(0, b'First Last (e.g. English)'), (1, b'Last First (e.g. East Asian names in English characters)'), (2, b'LastFirst (e.g. East Asian names in characters)')])),
                ('forum_last_act', models.DateTimeField(auto_now_add=True, verbose_name=b'Forum last activity')),
                ('email_careers_newsletter_AU_optin', models.BooleanField(default=False, verbose_name=b'Subscribe to Robogals Careers Newsletter - Australia')),
                ('aliases', models.ManyToManyField(related_name='user_aliases', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
                ('chapter', models.ForeignKey(default=1, to='rgchapter.Chapter')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('timezone', models.ForeignKey(verbose_name=b"Override chapter's timezone", blank=True, to='rgmain.Timezone', null=True)),
                ('tshirt', models.ForeignKey(blank=True, to='rgchapter.ShirtSize', null=True)),
                ('university', models.ForeignKey(blank=True, to='rgmain.University', null=True)),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MemberStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status_date_start', models.DateField(default=datetime.date.today, null=True, blank=True)),
                ('status_date_end', models.DateField(null=True, blank=True)),
            ],
            options={
                'ordering': ('-status_date_end', '-status_date_start'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MemberStatusType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=64)),
                ('type_of_person', models.IntegerField(default=0, choices=[(0, b'N/A'), (1, b'Student'), (2, b'Employed')])),
                ('chapter', models.ForeignKey(blank=True, to='rgchapter.Chapter', null=True)),
            ],
            options={
                'verbose_name': 'member status',
                'verbose_name_plural': 'member statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position_date_start', models.DateField(default=datetime.date.today)),
                ('position_date_end', models.DateField(null=True, blank=True)),
                ('positionChapter', models.ForeignKey(to='rgchapter.Chapter')),
            ],
            options={
                'ordering': ('-position_date_end', '-position_date_start'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PositionType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=64)),
                ('rank', models.IntegerField()),
                ('chapter', models.ForeignKey(blank=True, to='rgchapter.Chapter', null=True)),
            ],
            options={
                'ordering': ('rank',),
                'verbose_name': 'position type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('notes', models.TextField(blank=True)),
                ('chapter', models.ForeignKey(to='rgchapter.Chapter')),
                ('display_columns', models.ManyToManyField(to='rgchapter.DisplayColumn')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='position',
            name='positionType',
            field=models.ForeignKey(to='rgprofile.PositionType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='position',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memberstatus',
            name='statusType',
            field=models.ForeignKey(to='rgprofile.MemberStatusType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memberstatus',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
