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
            name='Conference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('details', models.TextField(blank=True)),
                ('url', models.CharField(help_text=b'URL to page with information', max_length=128)),
                ('committee_year', models.IntegerField(default=0, help_text=b'The committee year for the purposes of the relevant question in the RSVP form. Put 0 to remove this question from the form.')),
                ('early_rsvp_close', models.DateTimeField(help_text=b'Time in UTC when benefits for registering early should close (not implemented)')),
                ('rsvp_close', models.DateTimeField(help_text=b'Time in UTC when registration will close; set policy below. Publicly viewable.')),
                ('late_rsvp_close', models.DateTimeField(help_text=b'Time in UTC when late registration will close; set policy below. Not publicly viewable, so can be used to silently allow late RSVPs.')),
                ('timezone_desc', models.CharField(help_text=b"Description of timezone, e.g. 'Melbourne time' or 'Pacific Time'", max_length=128)),
                ('policy', models.IntegerField(default=1, choices=[(0, b'Registration to auto-close at RSVP deadline'), (1, b'Registration to auto-close at late RSVP deadline'), (2, b'Registraion open indefinitely'), (3, b'Registration closed'), (4, b'Conference closed and hidden from list')])),
                ('closed_msg', models.CharField(default=b'This form is now closed. To add/modify/remove RSVPs please email ______________', help_text=b'Message to be shown when registration is closed', max_length=128, blank=True)),
                ('enable_invoicing', models.BooleanField(default=False)),
                ('custom1_setting', models.IntegerField(default=0, choices=[(0, b'Disabled'), (1, b'Enabled, for use by organisers'), (2, b'Enabled, user-settable (not implemented)')])),
                ('custom1_label', models.CharField(max_length=32, blank=True)),
                ('custom2_setting', models.IntegerField(default=0, choices=[(0, b'Disabled'), (1, b'Enabled, for use by organisers'), (2, b'Enabled, user-settable (not implemented)')])),
                ('custom2_label', models.CharField(max_length=32, blank=True)),
                ('custom3_setting', models.IntegerField(default=0, choices=[(0, b'Disabled'), (1, b'Enabled, for use by organisers'), (2, b'Enabled, user-settable (not implemented)')])),
                ('custom3_label', models.CharField(max_length=32, blank=True)),
                ('custom4_setting', models.IntegerField(default=0, choices=[(0, b'Disabled'), (1, b'Enabled, for use by organisers'), (2, b'Enabled, user-settable (not implemented)')])),
                ('custom4_label', models.CharField(max_length=32, blank=True)),
                ('custom5_setting', models.IntegerField(default=0, choices=[(0, b'Disabled'), (1, b'Enabled, for use by organisers'), (2, b'Enabled, user-settable (not implemented)')])),
                ('custom5_label', models.CharField(max_length=32, blank=True)),
                ('host', models.ForeignKey(blank=True, to='rgchapter.Chapter', null=True)),
                ('timezone', models.ForeignKey(help_text=b'Timezone of the place where the conference is taking place. Used for RSVP deadlines', to='rgmain.Timezone')),
            ],
            options={
                'ordering': ('-start_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConferenceAttendee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('attendee_type', models.IntegerField(blank=True, null=True, choices=[(0, b'Outgoing from committee'), (1, b'Continuing in commmitee'), (2, b'Incoming into committee'), (3, b'None of the above; ordinary volunteer')])),
                ('outgoing_position', models.CharField(max_length=64, blank=True)),
                ('incoming_position', models.CharField(max_length=64, blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name=b'E-mail address')),
                ('mobile', models.CharField(max_length=32)),
                ('dob', models.DateField()),
                ('emergency_name', models.CharField(max_length=64)),
                ('emergency_number', models.CharField(max_length=32)),
                ('emergency_relationship', models.CharField(max_length=64)),
                ('arrival_time', models.CharField(max_length=64, blank=True)),
                ('dietary_reqs', models.CharField(max_length=64, blank=True)),
                ('comments', models.CharField(max_length=128, blank=True)),
                ('rsvp_time', models.DateTimeField(help_text=b'Time in conference timezone when this person registered (does not change if RSVP edited)', auto_now_add=True)),
                ('check_in', models.DateField(null=True, blank=True)),
                ('check_out', models.DateField(null=True, blank=True)),
                ('gender', models.IntegerField(default=0, choices=[(0, b'Unknown'), (1, b'Male'), (2, b'Female')])),
                ('custom1', models.BooleanField(default=False)),
                ('custom2', models.BooleanField(default=False)),
                ('custom3', models.BooleanField(default=False)),
                ('custom4', models.BooleanField(default=False)),
                ('custom5', models.BooleanField(default=False)),
                ('conference', models.ForeignKey(to='rgconf.Conference')),
            ],
            options={
                'ordering': ('conference', 'last_name', 'first_name'),
                'verbose_name': 'attendee',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConferenceCurrency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso_code', models.CharField(max_length=3, verbose_name=b'ISO code')),
                ('name', models.CharField(max_length=64)),
                ('symbol', models.CharField(max_length=8)),
                ('format', models.CharField(max_length=16)),
            ],
            options={
                'verbose_name': 'currency',
                'verbose_name_plural': 'currencies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConferencePart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('details', models.TextField(blank=True)),
                ('cost', models.DecimalField(max_digits=9, decimal_places=2)),
                ('gst_incl', models.BooleanField(default=True, verbose_name=b'GST included')),
                ('order', models.IntegerField()),
                ('conference', models.ForeignKey(to='rgconf.Conference')),
                ('currency', models.ForeignKey(to='rgconf.ConferenceCurrency')),
            ],
            options={
                'ordering': ('conference', 'order'),
                'verbose_name': 'part',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConferencePayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('amount', models.DecimalField(max_digits=9, decimal_places=2)),
                ('payment_method', models.IntegerField(default=1, choices=[(0, b'Other'), (1, b'Direct deposit'), (2, b'PayPal'), (3, b'Credit card'), (4, b'Cash'), (5, b'Cheque'), (6, b'Paid by Robogals')])),
                ('notes', models.TextField(blank=True)),
                ('attendee', models.ForeignKey(to='rgconf.ConferenceAttendee')),
                ('currency', models.ForeignKey(to='rgconf.ConferenceCurrency')),
            ],
            options={
                'ordering': ('-date',),
                'verbose_name': 'payment',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='conferenceattendee',
            name='parts_attending',
            field=models.ManyToManyField(to='rgconf.ConferencePart', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conferenceattendee',
            name='tshirt',
            field=models.ForeignKey(blank=True, to='rgchapter.ShirtSize', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conferenceattendee',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
