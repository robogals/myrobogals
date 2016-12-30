# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgmain', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('award_name', models.CharField(max_length=64)),
                ('award_type', models.IntegerField(default=0, choices=[(0, b'Major'), (1, b'Minor')])),
                ('award_description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('award_type', 'award_name'),
                'verbose_name': 'Award',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AwardRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(default=2000)),
                ('region', models.IntegerField(default=0, choices=[(0, b'Australia & New Zealand'), (1, b'UK & Europe'), (2, b'Asia Pacific'), (3, b'North America'), (4, b'EMEA')])),
                ('description', models.TextField(blank=True)),
                ('award', models.ForeignKey(to='rgchapter.Award')),
            ],
            options={
                'ordering': ('-year', 'award', 'region', 'chapter'),
                'verbose_name': 'Award recipient',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80, verbose_name=b'Name')),
                ('short', models.CharField(help_text=b'Use city name in local language (e.g. Melbourne) unless this is a regional body (e.g. Asia Pacific)', max_length=80, verbose_name=b'Short Name')),
                ('short_en', models.CharField(help_text=b'Use city name in English (e.g. Melbourne) unless this is a regional body (e.g. Asia Pacific)', max_length=80, verbose_name=b'English Short Name')),
                ('location', models.CharField(help_text=b'Use the format: City, Country (e.g. Melbourne, Australia); in the US also include state (e.g. Pasadena, California, USA)', max_length=64, verbose_name=b'Location', blank=True)),
                ('myrobogals_url', models.CharField(help_text=b'The chapter page will be https://my.robogals.org/chapters/&lt;url&gt;/ - our convention is to use lowercase city name in English', unique=True, max_length=16, verbose_name=b'myRobogals URL')),
                ('creation_date', models.DateField(help_text=b'Our convention is to use the first day of the SINE at which this chapter was founded')),
                ('status', models.IntegerField(default=2, choices=[(0, b'Active'), (1, b'Inactive'), (2, b'Hidden')])),
                ('address', models.TextField(help_text=b"Don't put city, state and postcode above, there's a spot for them right below", verbose_name=b'Postal address', blank=True)),
                ('city', models.CharField(max_length=64, verbose_name=b'City/Suburb', blank=True)),
                ('state', models.CharField(help_text=b"Use the abbreviation, e.g. 'VIC' not 'Victoria'", max_length=16, verbose_name=b'State/Province', blank=True)),
                ('postcode', models.CharField(max_length=16, verbose_name=b'Postcode', blank=True)),
                ('faculty_contact', models.CharField(help_text=b'e.g. Professor John Doe', max_length=64, verbose_name=b'Name', blank=True)),
                ('faculty_position', models.CharField(help_text=b'e.g. Associate Dean', max_length=64, verbose_name=b'Position', blank=True)),
                ('faculty_department', models.CharField(help_text=b'e.g. Faculty of Engineering', max_length=64, verbose_name=b'Department', blank=True)),
                ('faculty_email', models.CharField(max_length=64, verbose_name=b'Email', blank=True)),
                ('faculty_phone', models.CharField(help_text=b'International format, e.g. +61 3 8344 4000', max_length=32, verbose_name=b'Phone', blank=True)),
                ('website_url', models.CharField(max_length=128, verbose_name=b'Website URL', blank=True)),
                ('facebook_url', models.CharField(max_length=128, verbose_name=b'Facebook URL', blank=True)),
                ('is_joinable', models.BooleanField(default=True, help_text=b'People can join this chapter through the website. Untick this box for regional bodies, e.g. Robogals Asia Pacific.', verbose_name=b'Joinable')),
                ('infobox', models.TextField(blank=True)),
                ('photo', models.FileField(help_text=b'This must be scaled down before uploading. It should be exactly 320px wide, and while the height can vary, it should be oriented landscape.', upload_to=b'unipics', blank=True)),
                ('emailtext', models.TextField(verbose_name=b'Default email reminder text', blank=True)),
                ('smstext', models.TextField(verbose_name=b'Default SMS reminder text', blank=True)),
                ('upload_exec_list', models.BooleanField(default=False, verbose_name=b'Enable daily FTP upload of executive committee list')),
                ('ftp_host', models.CharField(max_length=64, verbose_name=b'FTP host', blank=True)),
                ('ftp_user', models.CharField(max_length=64, verbose_name=b'FTP username', blank=True)),
                ('ftp_pass', models.CharField(max_length=64, verbose_name=b'FTP password', blank=True)),
                ('ftp_path', models.CharField(help_text=b'Including directory and filename, e.g. web/content/team.html', max_length=64, verbose_name=b'FTP path', blank=True)),
                ('student_number_enable', models.BooleanField(default=False, verbose_name=b'Enable student number field')),
                ('student_number_required', models.BooleanField(default=False, verbose_name=b'Require student number field')),
                ('student_number_label', models.CharField(max_length=64, verbose_name=b'Label for student number field', blank=True)),
                ('student_union_enable', models.BooleanField(default=False, verbose_name=b'Enable student union member checkbox')),
                ('student_union_required', models.BooleanField(default=False, verbose_name=b'Require student union member checkbox')),
                ('student_union_label', models.CharField(max_length=64, verbose_name=b'Label for student union member checkbox', blank=True)),
                ('welcome_email_enable', models.BooleanField(default=True, verbose_name=b'Enable welcome email for new signups')),
                ('welcome_email_subject', models.CharField(default=b'Welcome to Robogals!', max_length=128, verbose_name=b'Subject', blank=True)),
                ('welcome_email_msg', models.TextField(default=b'Dear {user.first_name},\n\nThankyou for joining {chapter.name}!\n\nYour username and password for myRobogals can be found below:\n\nUsername: {user.username}\nPassword: {plaintext_password}\nLogin at https://my.robogals.org\n\nRegards,\n\n{chapter.name}\n', verbose_name=b'Message', blank=True)),
                ('welcome_email_html', models.BooleanField(default=False, verbose_name=b'HTML')),
                ('invite_email_subject', models.CharField(default=b'Upcoming Robogals workshop', max_length=128, verbose_name=b'Subject', blank=True)),
                ('invite_email_msg', models.TextField(default=b'Hello,\n\n{visit.chapter.name} will be conducting a workshop soon:\nWhen: {visit.visit_time}\nLocation: {visit.location}\nSchool: {visit.school.name}\n\nFor more information, and to accept or decline this invitation to volunteer at this workshop, please visit https://my.robogals.org/teaching/{visit.pk}/\n\nThanks,\n\n{user.first_name}', verbose_name=b'Message', blank=True)),
                ('invite_email_html', models.BooleanField(default=False, verbose_name=b'HTML')),
                ('welcome_page', models.TextField(default=b'Congratulations on becoming a member of {chapter.name}, and welcome to the international network of Robogals members - students around the world committed to increasing female participation in engineering!<br>\n<br>\nYour member account has been created - simply log in using the form to the left.', verbose_name=b'Welcome page HTML', blank=True)),
                ('join_page', models.TextField(help_text=b'This page is shown if the chapter is not joinable via myRobogals. It should explain how to join this chapter, e.g. who to contact.', verbose_name=b'Join page HTML', blank=True)),
                ('notify_enable', models.BooleanField(default=False, verbose_name=b'Notify when a new member signs up online')),
                ('sms_limit', models.IntegerField(default=1000, verbose_name=b'Monthly SMS limit')),
                ('tshirt_enable', models.BooleanField(default=False, verbose_name=b'Enable T-shirt drop-down')),
                ('tshirt_required', models.BooleanField(default=False, verbose_name=b'Require T-shirt drop-down')),
                ('tshirt_label', models.CharField(max_length=64, verbose_name=b'Label for T-shirt drop-down', blank=True)),
                ('name_display', models.IntegerField(default=0, help_text=b'Most Asian chapters have used English names in myRobogals, despite this option being available. Check with the chapter before modifying.', verbose_name=b'Name display', choices=[(0, b'First Last (e.g. English)'), (1, b'Last First (e.g. East Asian names in English characters)'), (2, b'LastFirst (e.g. East Asian names in characters)')])),
                ('goal', models.IntegerField(default=0, null=True, verbose_name=b'Goal', blank=True)),
                ('goal_start', models.DateField(help_text=b'Our convention is to use the first day of the SINE at which they set their current-year goal', null=True, verbose_name=b'Goal start date', blank=True)),
                ('exclude_in_reports', models.BooleanField(default=False, verbose_name=b'Exclude this chapter in global reports')),
                ('latitude', models.FloatField(help_text=b'If blank, will be automatically filled in by Google Maps API when this chapter is made active. Value can be entered here manually if necessary.', null=True, blank=True)),
                ('longitude', models.FloatField(help_text=b'If blank, will be automatically filled in by Google Maps API when this chapter is made active. Value can be entered here manually if necessary.', null=True, blank=True)),
                ('country', models.ForeignKey(default=b'AU', blank=True, to='rgmain.Country', null=True, verbose_name=b'Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DisplayColumn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_name', models.CharField(max_length=64)),
                ('display_name_en', models.CharField(max_length=64)),
                ('display_name_nl', models.CharField(max_length=64, blank=True)),
                ('display_name_ja', models.CharField(max_length=64, blank=True)),
                ('order', models.IntegerField(default=10)),
            ],
            options={
                'ordering': ('order', 'field_name'),
                'verbose_name': 'Column display name',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShirtSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size_short', models.CharField(max_length=32)),
                ('size_long', models.CharField(max_length=64)),
                ('order', models.IntegerField(default=10)),
                ('chapter', models.ForeignKey(to='rgchapter.Chapter')),
            ],
            options={
                'ordering': ('chapter', 'order', 'size_long'),
                'verbose_name': 'T-shirt size',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='chapter',
            name='display_columns',
            field=models.ManyToManyField(help_text=b'When creating a new chapter, you MUST populate this! Recommendation: get_full_name, email, mobile.', to='rgchapter.DisplayColumn'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chapter',
            name='mobile_regexes',
            field=models.ForeignKey(to='rgmain.MobileRegexCollection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chapter',
            name='parent',
            field=models.ForeignKey(verbose_name=b'Parent', blank=True, to='rgchapter.Chapter', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chapter',
            name='timezone',
            field=models.ForeignKey(help_text=b"Timezones are ordered by continent/city. If the chapter's city is not listed, select a city in the same timezone with the same daylight saving rules. Do NOT select an exact offset like GMT+10, as this will not take daylight saving time into account. Note that the UK is not on GMT during summer - select Europe/London to get the correct daylight saving rules for the UK.", to='rgmain.Timezone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chapter',
            name='university',
            field=models.ForeignKey(blank=True, to='rgmain.University', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='awardrecipient',
            name='chapter',
            field=models.ForeignKey(to='rgchapter.Chapter'),
            preserve_default=True,
        ),
    ]
