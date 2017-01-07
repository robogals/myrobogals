from django.contrib.auth.models import AbstractUser
from django.utils.encoding import smart_str
from django.db import models, connection
from myrobogals.rgchapter.models import Chapter, DisplayColumn, ShirtSize, NAME_DISPLAYS
from myrobogals.rgmain.models import University, Timezone
from myrobogals.settings import GENDERS
from datetime import date
from urllib import quote

class MemberStatusType(models.Model):
	PERSONTYPES = (
		(0, 'N/A'),
		(1, 'Student'),
		(2, 'Employed'),
	)
	description = models.CharField(max_length=64)
	chapter = models.ForeignKey(Chapter, null=True, blank=True)
	
	def idstr(self):
		return str(self.id)

	def __unicode__(self):
		return self.description
	
	class Meta:
		verbose_name = "member status"
		verbose_name_plural = "member statuses"

class MemberStatus(models.Model):
	user = models.ForeignKey('User')
	statusType = models.ForeignKey(MemberStatusType)
	status_date_start = models.DateField(default=date.today, null=True, blank=True)
	status_date_end = models.DateField(null=True, blank=True)

	def __unicode__(self):
		if (self.status_date_end):
			return self.statusType.description + " (" + self.status_date_start.strftime("%b %Y") + " - " + self.status_date_end.strftime("%b %Y") + ")"
		else:
			return self.statusType.description + " (" + self.status_date_start.strftime("%b %Y") + " - present)"

	class Meta:
		ordering = ('-status_date_end', '-status_date_start')

class PositionType(models.Model):
	description = models.CharField(max_length=64)
	chapter = models.ForeignKey(Chapter, null=True, blank=True)
	rank = models.IntegerField()

	def __unicode__(self):
		return self.description

	class Meta:
		verbose_name = "position type"
		ordering = ('rank',)

class Position(models.Model):
	user = models.ForeignKey('rgprofile.User')
	positionType = models.ForeignKey(PositionType)
	positionChapter = models.ForeignKey(Chapter)
	position_date_start = models.DateField(default=date.today)
	position_date_end = models.DateField(null=True, blank=True)

	def __unicode__(self):
		if (self.position_date_end):
			return self.positionType.description + ", " + self.positionChapter.name + " (" + self.position_date_start.strftime("%b %Y") + " - " + self.position_date_end.strftime("%b %Y") + ")"
		else:
			return self.positionType.description + ", " + self.positionChapter.name + " (" + self.position_date_start.strftime("%b %Y") + " - present)"

	class Meta:
		ordering = ('-position_date_end', '-position_date_start')

class User(AbstractUser):
	PRIVACY_CHOICES = (
		(20, 'Public'),
		(10, 'Only Robogals members can see'),
		(5, 'Only Robogals members in my chapter can see'),
		(0, 'Private (only committee can see)'),
	)
	
	COURSE_TYPE_CHOICES = (
		(0, 'No answer'),
		(1, 'Undergraduate'),
		(2, 'Postgraduate'),
	)

	STUDENT_TYPE_CHOICES = (
		(0, 'No answer'),
		(1, 'Local'),
		(2, 'International'),
	)

	chapter = models.ForeignKey(Chapter, default=1)
	alt_email = models.EmailField('Alternate e-mail address', blank=True)
	dob = models.DateField(null=True, blank=True)
	dob_public = models.BooleanField("Display date of birth in profile", default=False)
	email_public = models.BooleanField("Display email address in profile", default=False)
	course = models.CharField('Course', max_length=64, blank=True)
	uni_start = models.DateField(null=True, blank=True)
	uni_end = models.DateField(null=True, blank=True)
	university = models.ForeignKey(University, null=True, blank=True)
	job_title = models.CharField('Job title', max_length=128, blank=True)
	company = models.CharField('Company', max_length=128, blank=True)
	mobile = models.CharField('Mobile', max_length=16, blank=True)
	mobile_verified = models.BooleanField(default=False)
	email_reminder_optin = models.BooleanField("Allow email reminders", default=True)
	email_chapter_optin = models.BooleanField("Allow emails from chapter", default=True)
	mobile_reminder_optin = models.BooleanField("Allow mobile reminders", default=True)
	mobile_marketing_optin = models.BooleanField("Allow mobile marketing", default=False)
	email_newsletter_optin = models.BooleanField("Subscribe to The Amplifier", default=True)
	email_othernewsletter_optin = models.BooleanField("Subscribe to alumni newsletter (if alumni)", default=True, help_text="Ignored unless this user is actually alumni.  It is recommended that you leave this ticked so that the user will automatically be subscribed upon becoming alumni.")
	timezone = models.ForeignKey(Timezone, verbose_name="Override chapter's timezone", blank=True, null=True)
	photo = models.FileField(upload_to='profilepics', blank=True)
	bio = models.TextField(blank=True)
	internal_notes = models.TextField(blank=True)
	website = models.CharField("Personal website", max_length=200, blank=True)
	gender = models.IntegerField("Gender", choices=GENDERS, default=0)
	privacy = models.IntegerField("Profile privacy", choices=PRIVACY_CHOICES, default=5)
	course_type = models.IntegerField("Course level", choices=COURSE_TYPE_CHOICES, default=0)
	student_type = models.IntegerField("Student type", choices=STUDENT_TYPE_CHOICES, default=0)
	student_number = models.CharField('Student number', max_length=32, blank=True)
	union_member = models.BooleanField(default=False)
	tshirt = models.ForeignKey(ShirtSize, null=True, blank=True)
	trained = models.BooleanField(default=False)
	security_check = models.BooleanField(default=False)
	name_display = models.IntegerField("Override chapter's name display", choices=NAME_DISPLAYS, blank=True, null=True)
	forum_last_act = models.DateTimeField('Forum last activity', auto_now_add=True)
	aliases = models.ManyToManyField('User', blank=True, null=True, related_name='user_aliases')
	email_careers_newsletter_AU_optin = models.BooleanField("Subscribe to Robogals Careers Newsletter - Australia", default=False)

	def __unicode__(self):
		return self.username
	
	def age(self):
		return int((date.today() - self.dob).days / 365.25)
	
	# This fixes members whose MemberStatus is broken.
	# It returns the new value.
	def fixmembertype(self):
		# Get all types ever assigned to this member
		ms_list = MemberStatus.objects.filter(user=self).order_by('status_date_end',)
		n_total = len(ms_list)
		if n_total == 0:
			# This member never had a type
			# Create the type "Volunteer" effective from join date
			volunteer = MemberStatusType.objects.get(pk=1)
			ms = MemberStatus(user=self, status_date_start=self.date_joined.date(), status_date_end=None, statusType=volunteer)
			ms.save()
			return student
		else:
			# Get all types currently active on this member (should not be more than one)
			ms_active_list = MemberStatus.objects.filter(user=self, status_date_end__isnull=True).order_by('status_date_start',)
			n_active = len(ms_active_list)
			if n_active > 1:
				# This member has more than one active type
				# Deactivate all but the last type
				for i in range(n_active-1):
					ms = ms_active_list[i]
					ms.status_date_end = datetime.datetime.now().date()
					ms.save()
				# Return the active status (i.e. last in the list)
				return ms_active_list[n_active-1].statusType
			elif n_active < 1:
				# This member has old types but no current types
				# Make the most recently ended type the current type
				ms = ms_list[n_total-1]
				ms.status_date_end = None
				ms.save()
				return ms.statusType
			else:
				# This user is not actually broken
				# Return the actual current type
				return ms_active_list[0].statusType

	# Return current member type
	def membertype(self):
		try:
			return MemberStatus.objects.get(user=self, status_date_end__isnull=True).statusType
		except (MemberStatus.DoesNotExist, MemberStatus.MultipleObjectsReturned):
			# The member type is broken, fix it and return the fixed value
			return self.fixmembertype()

	# If they have set a timezone override, use that
	# otherwise use their chapter's timezone
	def tz_obj(self):
		if self.timezone:
			return self.timezone.tz_obj()
		else:
			return self.chapter.timezone.tz_obj()
	
	# Similar deal for name display
	def get_name_display(self):
		if self.name_display:
			return self.name_display
		else:
			return self.chapter.name_display

	def graduation_year(self):
		if self.uni_end:
			return self.uni_end.strftime("%Y")
		else:
			return ""

	def date_joined_local(self):
		return self.date_joined.astimezone(self.tz_obj())

	def get_absolute_url(self):
		return "/profile/%s/" % quote(smart_str(self.username))
	
	def get_full_name(self):
		if self.get_name_display() == 0:
			full_name = u'%s %s' % (self.first_name, self.last_name)
		elif self.get_name_display() == 1:
			full_name = u'%s %s' % (self.last_name, self.first_name)
		elif self.get_name_display() == 2:
			full_name = u'%s%s' % (self.last_name, self.first_name)
		return full_name.strip()
	
	def has_cur_pos(self):
		cursor = connection.cursor()
		cursor.execute('SELECT COUNT(user_id) FROM `rgprofile_position` WHERE user_id = ' + str(self.pk) + ' AND position_date_end IS NULL')
		ms = cursor.fetchone()
		if ms[0] > 0:
		   return True
		else:
		   return False

	def cur_positions(self):
		return Position.objects.filter(user=self, position_date_end__isnull=True)

	def has_robogals_email(self):
		try:
			domain = self.email.split('@', 1)[1]
			return domain == 'robogals.org'
		except IndexError:
			return False

class UserList(models.Model):
	name = models.CharField(max_length=128)
	chapter = models.ForeignKey(Chapter)
	users = models.ManyToManyField(User)
	display_columns = models.ManyToManyField(DisplayColumn)
	notes = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.name

# Import and register the signal handlers in signals.py
import signals
