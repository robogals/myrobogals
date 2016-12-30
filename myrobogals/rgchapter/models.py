from django.db import models
from django.utils import translation
from myrobogals.rgmain.models import University, Country, Timezone
from myrobogals.rgmessages.models_mobileregex import MobileRegexCollection
from django.db import connection
import datetime
from pytz import utc
from django.utils.timezone import make_aware

class DisplayColumn(models.Model):
	field_name = models.CharField(max_length=64)
	display_name_en = models.CharField(max_length=64)
	display_name_nl = models.CharField(max_length=64, blank=True)
	display_name_ja = models.CharField(max_length=64, blank=True)
	order = models.IntegerField(default=10)
	
	def __unicode__(self):
		return self.field_name
	
	def display_name_local(self):
		return getattr(self, "display_name_" + translation.get_language())
	
	class Meta:
		ordering = ('order','field_name')
		verbose_name = "Column display name"

NAME_DISPLAYS = (
	(0, 'First Last (e.g. English)'),
	(1, 'Last First (e.g. East Asian names in English characters)'),
	(2, 'LastFirst (e.g. East Asian names in characters)')
)

class Chapter(models.Model):
	STATUS_CHOICES = (
		(0, 'Active'),
		(1, 'Inactive'),
		(2, 'Hidden'),
	)

	name = models.CharField('Name', max_length=80, unique=True)
	short = models.CharField('Short Name', max_length=80, help_text='Use city name in local language (e.g. Melbourne) unless this is a regional body (e.g. Asia Pacific)')
	short_en = models.CharField('English Short Name', max_length=80, help_text='Use city name in English (e.g. Melbourne) unless this is a regional body (e.g. Asia Pacific)')
	location = models.CharField('Location', help_text='Use the format: City, Country (e.g. Melbourne, Australia); in the US also include state (e.g. Pasadena, California, USA)', max_length=64, blank=True)
	myrobogals_url = models.CharField('myRobogals URL', max_length=16, unique=True, help_text="The chapter page will be https://my.robogals.org/chapters/&lt;url&gt;/ - our convention is to use lowercase city name in English")
	creation_date = models.DateField(help_text='Our convention is to use the first day of the SINE at which this chapter was founded')
	university = models.ForeignKey(University, null=True, blank=True)
	parent = models.ForeignKey('self', verbose_name='Parent', null=True, blank=True)
	status = models.IntegerField(choices=STATUS_CHOICES, default=2)
	address = models.TextField('Postal address', help_text="Don't put city, state and postcode above, there's a spot for them right below", blank=True)
	city = models.CharField('City/Suburb', max_length=64, blank=True)
	state = models.CharField('State/Province', max_length=16, help_text="Use the abbreviation, e.g. 'VIC' not 'Victoria'", blank=True)
	postcode = models.CharField('Postcode', max_length=16, blank=True)
	country = models.ForeignKey(Country, verbose_name="Country", default="AU", blank=True, null=True)
	timezone = models.ForeignKey(Timezone, help_text="Timezones are ordered by continent/city. If the chapter's city is not listed, select a city in the same timezone with the same daylight saving rules. Do NOT select an exact offset like GMT+10, as this will not take daylight saving time into account. Note that the UK is not on GMT during summer - select Europe/London to get the correct daylight saving rules for the UK.")
	faculty_contact = models.CharField('Name', max_length=64, blank=True, help_text="e.g. Professor John Doe")
	faculty_position = models.CharField('Position', max_length=64, blank=True, help_text="e.g. Associate Dean")
	faculty_department = models.CharField('Department', max_length=64, blank=True, help_text="e.g. Faculty of Engineering")
	faculty_email = models.CharField('Email', max_length=64, blank=True)
	faculty_phone = models.CharField('Phone', max_length=32, blank=True, help_text="International format, e.g. +61 3 8344 4000")
	website_url = models.CharField('Website URL', max_length=128, blank=True)
	facebook_url = models.CharField('Facebook URL', max_length=128, blank=True)
	is_joinable = models.BooleanField('Joinable', default=True, help_text='People can join this chapter through the website. Untick this box for regional bodies, e.g. Robogals Asia Pacific.')
	infobox = models.TextField(blank=True)
	photo = models.FileField(upload_to='unipics', blank=True, help_text='This must be scaled down before uploading. It should be exactly 320px wide, and while the height can vary, it should be oriented landscape.')
	emailtext = models.TextField('Default email reminder text', blank=True)
	smstext = models.TextField('Default SMS reminder text', blank=True)
	upload_exec_list = models.BooleanField('Enable daily FTP upload of executive committee list', default=False)
	ftp_host = models.CharField('FTP host', max_length=64, blank=True)
	ftp_user = models.CharField('FTP username', max_length=64, blank=True)
	ftp_pass = models.CharField('FTP password', max_length=64, blank=True)
	ftp_path = models.CharField('FTP path', max_length=64, blank=True, help_text='Including directory and filename, e.g. web/content/team.html')
	mobile_regexes = models.ForeignKey(MobileRegexCollection)
	student_number_enable = models.BooleanField('Enable student number field', default=False)
	student_number_required = models.BooleanField('Require student number field', default=False)
	student_number_label = models.CharField('Label for student number field', max_length=64, blank=True)
	student_union_enable = models.BooleanField('Enable student union member checkbox', default=False)
	student_union_required = models.BooleanField('Require student union member checkbox', default=False)
	student_union_label = models.CharField('Label for student union member checkbox', max_length=64, blank=True)
	welcome_email_enable = models.BooleanField('Enable welcome email for new signups', default=True)
	welcome_email_subject = models.CharField('Subject', max_length=128, blank=True, default='Welcome to Robogals!')
	welcome_email_msg = models.TextField('Message', blank=True, default="Dear {user.first_name},\n\nThankyou for joining {chapter.name}!\n\nYour username and password for myRobogals can be found below:\n\nUsername: {user.username}\nPassword: {plaintext_password}\nLogin at https://my.robogals.org\n\nRegards,\n\n{chapter.name}\n")
	welcome_email_html = models.BooleanField('HTML', default=False)
	invite_email_subject = models.CharField('Subject', max_length=128, blank=True, default="Upcoming Robogals workshop")
	invite_email_msg = models.TextField('Message', blank=True, default="Hello,\n\n{visit.chapter.name} will be conducting a workshop soon:\nWhen: {visit.visit_time}\nLocation: {visit.location}\nSchool: {visit.school.name}\n\nFor more information, and to accept or decline this invitation to volunteer at this workshop, please visit https://my.robogals.org/teaching/{visit.pk}/\n\nThanks,\n\n{user.first_name}")
	invite_email_html = models.BooleanField('HTML', default=False)
	welcome_page = models.TextField('Welcome page HTML', blank=True, default="Congratulations on becoming a member of {chapter.name}, and welcome to the international network of Robogals members - students around the world committed to increasing female participation in engineering!<br>\n<br>\nYour member account has been created - simply log in using the form to the left.")
	join_page = models.TextField('Join page HTML', blank=True, help_text='This page is shown if the chapter is not joinable via myRobogals. It should explain how to join this chapter, e.g. who to contact.')
	notify_enable = models.BooleanField('Notify when a new member signs up online', default=False)
	notify_list = models.ForeignKey('rgprofile.UserList', verbose_name='Who to notify', blank=True, null=True, related_name='chapter_notify_list')
	sms_limit = models.IntegerField('Monthly SMS limit', default=1000)
	display_columns = models.ManyToManyField(DisplayColumn, help_text='When creating a new chapter, you MUST populate this! Recommendation: get_full_name, email, mobile.')
	tshirt_enable = models.BooleanField('Enable T-shirt drop-down', default=False)
	tshirt_required = models.BooleanField('Require T-shirt drop-down', default=False)
	tshirt_label = models.CharField('Label for T-shirt drop-down', max_length=64, blank=True)
	name_display = models.IntegerField("Name display", choices=NAME_DISPLAYS, default=0, help_text='Most Asian chapters have used English names in myRobogals, despite this option being available. Check with the chapter before modifying.')
	goal = models.IntegerField("Goal", default=0, blank=True, null=True)
	goal_start = models.DateField("Goal start date", blank=True, null=True, help_text='Our convention is to use the first day of the SINE at which they set their current-year goal')
	exclude_in_reports = models.BooleanField('Exclude this chapter in global reports', default=False)
	latitude = models.FloatField(blank=True, null=True, help_text='If blank, will be automatically filled in by Google Maps API when this chapter is made active. Value can be entered here manually if necessary.')
	longitude = models.FloatField(blank=True, null=True, help_text='If blank, will be automatically filled in by Google Maps API when this chapter is made active. Value can be entered here manually if necessary.')
	
	@property
	def goal_start_tzaware(self):
		# Return a timezone-aware datetime equal to midnight on goal_start in the chapter's local time
		return make_aware(datetime.datetime.combine(self.goal_start, datetime.time.min), timezone=self.tz_obj())
	
	def __unicode__(self):
		return self.name
	
	# N.B. this function only works with three levels or less
	def do_membercount(self, type):
		cursor = connection.cursor()
		cursor.execute('SELECT id FROM rgchapter_chapter WHERE parent_id = ' + str(self.pk))
		ids_csv = ''
		while (1):
			ids = cursor.fetchone()
			if ids:
				ids_csv = ids_csv + ', ' + str(ids[0])
			else:
				break
		if ids_csv:
			cursor.execute('SELECT id FROM rgchapter_chapter WHERE parent_id IN (0' + ids_csv + ')')
			while (1):
				ids = cursor.fetchone()
				if ids:
					ids_csv = ids_csv + ', ' + str(ids[0])
				else:
					break
		if type == 0:
			cursor.execute('SELECT COUNT(id) FROM rgprofile_user WHERE is_active = 1 AND chapter_id IN (' + str(self.pk) + ids_csv + ')')
		else:
			cursor.execute('SELECT COUNT(u.id) FROM rgprofile_user AS u, rgprofile_memberstatus AS ms WHERE u.is_active = 1 AND u.chapter_id IN (' + str(self.pk) + ids_csv + ') AND u.id = ms.user_id AND ms.statusType_id = ' + str(type) + ' AND ms.status_date_end IS NULL')
		count = cursor.fetchone()
		if count:
			return int(count[0])
		else:
			return 0

	def membercount(self):
		return self.do_membercount(0)

	def membercount_student(self):
		return self.do_membercount(1)

	def local_time(self):
		return datetime.datetime.utcnow().replace(tzinfo=utc).astimezone(self.timezone.tz_obj())
	
	def tz_obj(self):
		return self.timezone.tz_obj()
	
	def get_absolute_url(self):
		return "/chapters/%s/" % self.myrobogals_url

	def save(self, *args, **kwargs):
		if (self.status == 0) and (self.university != None) and ((self.latitude == None) or (self.longitude == None)):
			try:
				data = {}
				data['address'] = self.university.name + ', ' + self.location
				data['sensor'] = 'false'
				url_values = urllib.urlencode(data)
				url = 'http://maps.googleapis.com/maps/api/geocode/json'
				full_url = url + '?' + url_values
				data = urllib2.urlopen(full_url, timeout=2)
				result = json.loads(data.read())
				if result['status'] == 'OK':
					self.latitude = result['results'][0]['geometry']['location']['lat']
					self.longitude = result['results'][0]['geometry']['location']['lng']
			except:
				pass
		super(Chapter, self).save(*args, **kwargs)

class ShirtSize(models.Model):
	size_short = models.CharField(max_length=32)
	size_long = models.CharField(max_length=64)
	chapter = models.ForeignKey(Chapter)
	order = models.IntegerField(default=10)
	
	def __unicode__(self):
		return self.size_short
	
	class Meta:
		ordering = ('chapter', 'order', 'size_long')
		verbose_name = "T-shirt size"

class Award(models.Model):
	AWARD_TYPE_CHOICES = (
		(0, 'Major'),
		(1, 'Minor')
	)
	
	award_name = models.CharField(max_length=64)
	award_type = models.IntegerField(choices=AWARD_TYPE_CHOICES, default=0)
	award_description = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.award_name
		
	class Meta:
		ordering = ('award_type', 'award_name')
		verbose_name = "Award"
		
REGION_CHOICES = (
	(0, 'Australia & New Zealand'),
	(1, 'UK & Europe'),
	(2, 'Asia Pacific'),
	(3, 'North America'),
	(4, 'EMEA'),
)

class AwardRecipient(models.Model):
	award = models.ForeignKey(Award)
	chapter = models.ForeignKey(Chapter)
	year = models.IntegerField(default=2000)
	region = models.IntegerField(choices=REGION_CHOICES, default=0)
	description = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.award.award_name
		
	class Meta:
		ordering = ('-year', 'award', 'region', 'chapter')
		verbose_name = "Award recipient"
