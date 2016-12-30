# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rgchapter', '0002_chapter_notify_list'),
        ('rgmain', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectorySchool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('address_street', models.CharField(max_length=128, blank=True)),
                ('address_city', models.CharField(max_length=64, verbose_name=b'city', blank=True)),
                ('address_postcode', models.CharField(max_length=16, verbose_name=b'postcode', blank=True)),
                ('email', models.CharField(max_length=64, blank=True)),
                ('phone', models.CharField(max_length=32, blank=True)),
                ('type', models.IntegerField(blank=True, null=True, choices=[(0, b'Government'), (1, b'Catholic'), (2, b'Independent')])),
                ('level', models.IntegerField(blank=True, null=True, choices=[(0, b'Combined'), (1, b'Primary'), (2, b'Secondary')])),
                ('gender', models.IntegerField(blank=True, null=True, choices=[(0, b'Coed'), (1, b'Boys'), (2, b'Girls')])),
                ('religion', models.CharField(max_length=32, blank=True)),
                ('asd_id', models.IntegerField(null=True, blank=True)),
                ('asd_feature', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('address_country', models.ForeignKey(default=b'AU', verbose_name=b'country', to='rgmain.Country')),
                ('address_state', models.ForeignKey(verbose_name=b'state', blank=True, to='rgmain.Subdivision', null=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visit_start', models.DateTimeField(verbose_name=b'Start')),
                ('visit_end', models.DateTimeField(verbose_name=b'End')),
                ('location', models.CharField(max_length=128, blank=True)),
                ('meeting_location', models.CharField(help_text=b'Where people can meet to go as a group to the final location, if applicable', max_length=128, blank=True)),
                ('meeting_time', models.DateTimeField(null=True, blank=True)),
                ('contact', models.CharField(max_length=128, blank=True)),
                ('contact_email', models.CharField(max_length=128, blank=True)),
                ('contact_phone', models.CharField(help_text=b'Mobile number to call if people get lost', max_length=32, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Open'), (1, b'Closed')])),
                ('allow_rsvp', models.IntegerField(default=0, choices=[(0, b'Allow anyone to RSVP'), (1, b'Only allow invitees to RSVP'), (2, b'Do not allow anyone to RSVP')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventAttendee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rsvp_status', models.IntegerField(default=1, choices=[(0, b'N/A'), (1, b'Awaiting reply'), (2, b'Attending'), (3, b'Maybe attending'), (4, b'Not attending')])),
                ('actual_status', models.IntegerField(default=0, choices=[(0, b'N/A'), (1, b'Attended'), (2, b'Did not attend')])),
                ('hours', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('message', models.TextField(verbose_name=b'RSVP message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('address_street', models.CharField(max_length=128, blank=True)),
                ('address_city', models.CharField(max_length=64, verbose_name=b'City/Suburb', blank=True)),
                ('address_state', models.CharField(help_text=b"Use the abbreviation, e.g. 'VIC' not 'Victoria'", max_length=16, verbose_name=b'State/Province')),
                ('address_postcode', models.CharField(max_length=16, verbose_name=b'Postcode', blank=True)),
                ('contact_person', models.CharField(max_length=64, blank=True)),
                ('contact_position', models.CharField(max_length=64, blank=True)),
                ('contact_email', models.CharField(max_length=64, blank=True)),
                ('contact_phone', models.CharField(max_length=32, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('address_country', models.ForeignKey(default=b'AU', verbose_name=b'Country', to='rgmain.Country')),
                ('chapter', models.ForeignKey(to='rgchapter.Chapter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchoolVisit',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='rgteaching.Event')),
                ('numstudents', models.CharField(max_length=32, verbose_name=b'Number of girls', blank=True)),
                ('yearlvl', models.CharField(max_length=32, verbose_name=b'Year level of girls', blank=True)),
                ('numrobots', models.CharField(max_length=32, verbose_name=b'Number of robots', blank=True)),
                ('lessonnum', models.CharField(max_length=32, verbose_name=b'Lesson number', blank=True)),
                ('toprint', models.TextField(verbose_name=b'Materials to be printed', blank=True)),
                ('tobring', models.TextField(verbose_name=b'Stuff to bring', blank=True)),
                ('otherprep', models.TextField(verbose_name=b'Other preparation', blank=True)),
                ('closing_comments', models.TextField(verbose_name=b'Closing comments', blank=True)),
                ('school', models.ForeignKey(to='rgteaching.School')),
            ],
            options={
                'ordering': ['-visit_start'],
            },
            bases=('rgteaching.event',),
        ),
        migrations.CreateModel(
            name='SchoolVisitStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visit_type', models.IntegerField(choices=[(0, b'Robogals robotics workshop, metro area'), (7, b'Robogals robotics workshop, regional area'), (1, b'Robogals career talk'), (2, b'Robogals event'), (3, b'Non-Robogals robotics workshop'), (4, b'Non-Robogals career talk'), (5, b'Non-Robogals event'), (6, b'Other')])),
                ('primary_girls_first', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('primary_girls_repeat', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('primary_boys_first', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('primary_boys_repeat', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('high_girls_first', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('high_girls_repeat', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('high_boys_first', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('high_boys_repeat', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('other_girls_first', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('other_girls_repeat', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('other_boys_first', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('other_boys_repeat', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('notes', models.TextField(verbose_name=b'General Notes', blank=True)),
                ('visit', models.ForeignKey(editable=False, to='rgteaching.SchoolVisit')),
            ],
            options={
                'verbose_name': 'workshop stats',
                'verbose_name_plural': 'workshop stats',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StarSchoolDirectory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chapter', models.ForeignKey(to='rgchapter.Chapter')),
                ('school', models.ForeignKey(to='rgteaching.DirectorySchool')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainingSession',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='rgteaching.Event')),
            ],
            options={
                'verbose_name': 'training session',
            },
            bases=('rgteaching.event',),
        ),
        migrations.AddField(
            model_name='eventmessage',
            name='event',
            field=models.ForeignKey(to='rgteaching.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventmessage',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventattendee',
            name='event',
            field=models.ForeignKey(to='rgteaching.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventattendee',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='chapter',
            field=models.ForeignKey(to='rgchapter.Chapter'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
