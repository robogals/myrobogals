# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import myrobogals.rgmessages.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rgchapter', '0002_chapter_notify_list'),
        ('rgmain', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('emailfile', models.FileField(upload_to=b'email_uploads')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'Name')),
                ('upper_body', models.TextField(verbose_name=b'Upper Body')),
                ('lower_body', models.TextField(verbose_name=b'Lower Body')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=256, verbose_name=b'Subject')),
                ('body', models.TextField(verbose_name=b'Message Body')),
                ('from_name', models.CharField(max_length=64, verbose_name=b'From Name')),
                ('from_address', models.EmailField(max_length=75, verbose_name=b'From Address')),
                ('reply_address', models.CharField(max_length=64, verbose_name=b'Reply Address')),
                ('status', models.IntegerField(default=0, verbose_name=b'Status Code', choices=[(-1, b'Wait'), (0, b'Pending'), (1, b'Complete')])),
                ('date', models.DateTimeField(verbose_name=b'Time Sent (in UTC)')),
                ('html', models.BooleanField(default=False, verbose_name=b'HTML')),
                ('scheduled', models.BooleanField(default=False, verbose_name=b'Scheduled')),
                ('scheduled_date', models.DateTimeField(null=True, verbose_name=b'Scheduled date (as entered)', blank=True)),
                ('scheduled_date_type', models.IntegerField(default=1, verbose_name=b'Scheduled date type', choices=[(1, b"Sender's timezone"), (2, b"Recipient's timezone")])),
                ('email_type', models.IntegerField(default=0, verbose_name=b'Email type', choices=[(0, b'Normal'), (1, b'Forum')])),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('upload_files', models.ManyToManyField(related_name='emailmessage_upload_files', to='rgmessages.EmailFile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to_name', models.CharField(max_length=128, verbose_name=b'To Name', blank=True)),
                ('to_address', models.EmailField(max_length=75, verbose_name=b'To Email')),
                ('status', models.IntegerField(default=0, verbose_name=b'Status Code', choices=[(0, b'Pending'), (1, b'Sent'), (2, b'Bounced'), (3, b'No sender address'), (4, b'Invalid sender address'), (5, b'Invalid recipient address'), (6, b'Unknown error'), (7, b'Opened')])),
                ('scheduled_date', models.DateTimeField(null=True, verbose_name=b'Scheduled date (in UTC)', blank=True)),
                ('message', models.ForeignKey(to='rgmessages.EmailMessage')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessagesSettings',
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
            name='Newsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('from_name', models.CharField(max_length=128)),
                ('from_email', models.CharField(max_length=128)),
                ('confirm_email', models.TextField(blank=True)),
                ('confirm_subject', models.CharField(max_length=128, blank=True)),
                ('confirm_url', models.CharField(max_length=128, blank=True)),
                ('confirm_from_name', models.CharField(max_length=128, blank=True)),
                ('confirm_from_email', models.CharField(max_length=128, blank=True)),
                ('confirm_html', models.BooleanField(default=False)),
                ('confirm_from_user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('from_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('first_name', models.CharField(max_length=128, blank=True)),
                ('last_name', models.CharField(max_length=128, blank=True)),
                ('company', models.CharField(max_length=128, blank=True)),
                ('details_verified', models.BooleanField(default=True)),
                ('subscribed_date', models.DateTimeField(auto_now_add=True)),
                ('unsubscribed_date', models.DateTimeField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('country', models.ForeignKey(blank=True, to='rgmain.Country', null=True)),
                ('newsletter', models.ForeignKey(to='rgmessages.Newsletter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PendingNewsletterSubscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=128)),
                ('uniqid', models.CharField(max_length=64)),
                ('pending_since', models.DateTimeField(auto_now_add=True)),
                ('newsletter', models.ForeignKey(to='rgmessages.Newsletter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SMSMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(verbose_name=b'Message body')),
                ('senderid', models.CharField(max_length=32, verbose_name=b'Sender ID')),
                ('status', models.IntegerField(default=0, verbose_name=b'Status code', choices=[(-1, b'Wait'), (0, b'Pending'), (1, b'Complete'), (2, b'Error'), (3, b'Limits exceeded')])),
                ('date', models.DateTimeField(verbose_name=b'Date set (in UTC)')),
                ('unicode', models.BooleanField(default=False, verbose_name=b'Unicode')),
                ('split', models.IntegerField(default=1, verbose_name=b'Split')),
                ('scheduled', models.BooleanField(default=False, verbose_name=b'Scheduled')),
                ('scheduled_date', models.DateTimeField(null=True, verbose_name=b'Scheduled date (as entered)', blank=True)),
                ('scheduled_date_type', models.IntegerField(default=1, verbose_name=b'Scheduled date type', choices=[(1, b"Sender's timezone"), (2, b"Recipient's timezone")])),
                ('sms_type', models.IntegerField(default=0, verbose_name=b'SMS type', choices=[(0, b'Normal'), (1, b'Mobile verification')])),
                ('chapter', models.ForeignKey(blank=True, to='rgchapter.Chapter', null=True)),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'SMS message',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SMSRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to_number', models.CharField(max_length=16, verbose_name=b'To number')),
                ('status', models.IntegerField(default=0, verbose_name=b'Status code', choices=[(0, b'Pending'), (1, b'Processing'), (5, b'Unknown error'), (6, b'Cancelled'), (7, b'Number barred'), (9, b'Number invalid'), (10, b'SMS sent'), (11, b'SMS accepted by carrier'), (12, b'SMS delivered'), (13, b'SMS undeliverable'), (14, b'SMS expired'), (15, b'SMS deleted by carrier'), (16, b'SMS rejected by carrier'), (17, b'SMS in unknown state'), (18, b'Construction error'), (19, b'Limits exceeded'), (20, b'Temporary error at SMSC'), (21, b'Permanent error at SMSC'), (22, b'Request to SMSC timed out')])),
                ('gateway', models.IntegerField(default=0, verbose_name=b'Gateway', choices=[(0, b'Use default'), (1, b'SMSGlobal')])),
                ('gateway_msg_id', myrobogals.rgmessages.models.PositiveBigIntegerField(default=0, verbose_name=b'Gateway message ID')),
                ('gateway_err', models.IntegerField(default=0, verbose_name=b'Error code', choices=[(0, b'Unknown subscriber'), (10, b'Network time-out'), (100, b'Facility not supported'), (101, b'Unknown subscriber'), (102, b'Facility not provided'), (103, b'Call barred'), (104, b'Operation barred'), (105, b'SC congestion'), (106, b'Facility not supported'), (107, b'Absent subscriber'), (108, b'Delivery fail'), (109, b'Sc congestion'), (110, b'Protocol error'), (111, b'MS not equipped'), (112, b'Unknown SC'), (113, b'SC congestion'), (114, b'Illegal MS'), (115, b'MS not a subscriber'), (116, b'Error in MS'), (117, b'SMS lower layer not provisioned'), (118, b'System fail'), (512, b'Expired'), (513, b'Rejected'), (515, b'No route to destination'), (608, b'System error'), (610, b'Invalid source address'), (611, b'Invalid destination address'), (625, b'Unknown destination')])),
                ('scheduled_date', models.DateTimeField(null=True, verbose_name=b'Scheduled date (in UTC)', blank=True)),
                ('message', models.ForeignKey(to='rgmessages.SMSMessage')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriberType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=128)),
                ('order', models.IntegerField()),
                ('public', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'subscriber type',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='newslettersubscriber',
            name='subscriber_type',
            field=models.ForeignKey(blank=True, to='rgmessages.SubscriberType', null=True),
            preserve_default=True,
        ),
    ]
