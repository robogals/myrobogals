from django.db import models
from myrobogals.rgprofile.models import User
from myrobogals.rgchapter.models import Chapter
from myrobogals.rgmain.models import Country, Subdivision
from datetime import datetime
import json, urllib, urllib2
from django.utils.timezone import localtime

# A school added to myRobogals by a schools manager or similar.
# A workshop must be linked to a "school"
class School(models.Model):
	name = models.CharField(max_length=64)
	chapter = models.ForeignKey(Chapter)
	address_street = models.CharField(max_length=128,blank=True)
	address_city = models.CharField('City/Suburb',max_length=64,blank=True)
	address_state = models.CharField('State/Province',max_length=16, help_text="Use the abbreviation, e.g. 'VIC' not 'Victoria'")
	address_postcode = models.CharField('Postcode',max_length=16,blank=True)
	address_country = models.ForeignKey(Country, verbose_name="Country", default="AU")
	contact_person = models.CharField(max_length=64, blank=True)
	contact_position = models.CharField(max_length=64, blank=True)
	contact_email = models.CharField(max_length=64, blank=True)
	contact_phone = models.CharField(max_length=32, blank=True)
	notes = models.TextField(blank=True)

	def __unicode__(self):
		return self.name

# A school in the schools directory. This data is imported in bulk.
class DirectorySchool(models.Model):
	TYPE_CHOICES = (
		(0, 'Government'),
		(1, 'Catholic'),
		(2, 'Independent'),
	)

	LEVEL_CHOICES = (
		(0, 'Combined'),
		(1, 'Primary'),
		(2, 'Secondary'),
	)

	GENDER_CHOICES = (
		(0, 'Coed'),
		(1, 'Boys'),
		(2, 'Girls'),
	)

	name = models.CharField(max_length=64)
	address_street = models.CharField(max_length=128, blank=True)
	address_city = models.CharField('city', max_length=64, blank=True)
	address_state = models.ForeignKey(Subdivision, verbose_name="state", blank=True, null=True)
	address_postcode = models.CharField('postcode', max_length=16, blank=True)
	address_country = models.ForeignKey(Country, verbose_name="country", default="AU")
	email = models.CharField(max_length=64, blank=True)
	phone = models.CharField(max_length=32, blank=True)
	type = models.IntegerField(choices=TYPE_CHOICES, blank=True, null=True)
	level = models.IntegerField(choices=LEVEL_CHOICES, blank=True, null=True)
	gender = models.IntegerField(choices=GENDER_CHOICES, blank=True, null=True)
	religion = models.CharField(max_length=32, blank=True)
	asd_id = models.IntegerField(blank=True, null=True)
	asd_feature = models.BooleanField(default=False)
	notes = models.TextField(blank=True)
	latitude = models.FloatField(blank=True, null=True)
	longitude = models.FloatField(blank=True, null=True)

	def __unicode__(self):
		return self.name
	
	def state_code(self):
		return self.address_state.code
	
	class Meta:
		ordering = ('name',)

	# Automatically get latitude-longitude based on the street address
	def save(self, *args, **kwargs):
		if (self.latitude == None) or (self.longitude == None):
			try:
				data = {}
				data['address'] = self.address_street
				data['components'] = '|locality:' + self.address_city + '|administrative_area:' + self.state_code() + '|country:' + self.address_country_id + '|postal_code:' + self.address_postcode
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
		super(DirectorySchool, self).save(*args, **kwargs)

# Stores when a chapter has "starred" a school in the directory
class StarSchoolDirectory(models.Model):
	school = models.ForeignKey(DirectorySchool)
	chapter = models.ForeignKey(Chapter)

# Base class for all events (e.g. workshops, training sessions)
class Event(models.Model):
	STATUS_CHOICES = (
		(0, 'Open'),
		(1, 'Closed'),
	)
	
	ALLOW_RSVP_CHOICES = (
		(0, 'Allow anyone to RSVP'),
		(1, 'Only allow invitees to RSVP'),
		(2, 'Do not allow anyone to RSVP'),
	)

	chapter = models.ForeignKey(Chapter)
	creator = models.ForeignKey(User)
	visit_start = models.DateTimeField("Start")
	visit_end = models.DateTimeField("End")
	location = models.CharField(max_length=128, blank=True)
	meeting_location = models.CharField(max_length=128, blank=True, help_text="Where people can meet to go as a group to the final location, if applicable")
	meeting_time = models.DateTimeField(null=True, blank=True)
	contact = models.CharField(max_length=128, blank=True)
	contact_email = models.CharField(max_length=128, blank=True)
	contact_phone = models.CharField(max_length=32, blank=True, help_text="Mobile number to call if people get lost")
	notes = models.TextField(blank=True)
	status = models.IntegerField(choices=STATUS_CHOICES, default=0)
	allow_rsvp = models.IntegerField(choices=ALLOW_RSVP_CHOICES, default=0)
	
	@property
	def visit_time(self):
		start_time_local = localtime(self.visit_start, timezone=self.chapter.tz_obj())
		end_time_local = localtime(self.visit_end, timezone=self.chapter.tz_obj())
		return start_time_local.strftime('%B %d, %Y, %I:%M %p') + ' to ' + end_time_local.strftime('%I:%M %p')

# This model represents a workshop. Despite the historic model name "SchoolVisit", the
# user interface now uses the term "workshop", recognising that not all workshops
# involve visiting a school.
class SchoolVisit(Event):
	school = models.ForeignKey(School)
	numstudents = models.CharField("Number of girls", max_length=32, blank=True)
	yearlvl = models.CharField("Year level of girls", max_length=32, blank=True)
	numrobots = models.CharField("Number of robots", max_length=32, blank=True)
	lessonnum = models.CharField("Lesson number", max_length=32, blank=True)
	toprint = models.TextField("Materials to be printed", blank=True)
	tobring = models.TextField("Stuff to bring", blank=True)
	otherprep = models.TextField("Other preparation", blank=True)
	closing_comments = models.TextField("Closing comments", blank=True)

	def __unicode__(self):
		return unicode(self.school) + " on " + str(self.visit_start.date())
		
	def get_absolute_url(self):
		return "/teaching/%d/" % self.pk
	
	# Returns the attached stats object, if there is one
	def get_stats(self):
		try:
			return self.schoolvisitstats_set.all()[0]
		except IndexError:
			return None

	# Returns the type of workshop (e.g. "Robogals career talk")
	# This type is selected when the stats are entered in
	def get_type(self):
		stats = self.get_stats()
		if stats == None:
			return ""
		else:
			return stats.get_visit_type_display()
	
	# If stats have been entered, returns the number of girls taught at this workshop
	def get_num_girls_display(self):
		stats = self.get_stats()
		if stats == None:
			return ""
		else:
			return str(stats.num_girls())
	
	class Meta:
		ordering = ['-visit_start']

# A message left on the event page. A user RSVPing to an event may optionally leave a message.
class EventMessage(models.Model):
	event = models.ForeignKey(Event)
	user = models.ForeignKey(User)
	date = models.DateTimeField()
	message = models.TextField("RSVP message")

# Class that inherits from Event, to represent a training session for volunteers.
# Not currently used.
class TrainingSession(Event):
	def __unicode__(self):
		return "Training session at " + self.location + " by " + str(self.chapter) + " on " + str(self.visit_start.date())
	
	class Meta:
		verbose_name = "training session"

# Model used to record RSVPs (while event open) and actual attendance (after event closed)
class EventAttendee(models.Model):
    RSVP_STATUS_CHOICES = (
    	(0, 'N/A'),
    	(1, 'Awaiting reply'),
    	(2, 'Attending'),
    	(3, 'Maybe attending'),
    	(4, 'Not attending'),
    )
    
    ACTUAL_STATUS_CHOICES = (
    	(0, 'N/A'),
    	(1, 'Attended'),
    	(2, 'Did not attend'),
    )
    
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    rsvp_status = models.IntegerField(choices=RSVP_STATUS_CHOICES, default=1)
    actual_status = models.IntegerField(choices=ACTUAL_STATUS_CHOICES, default=0)
    hours = models.IntegerField(default=0)
    
    def __unicode__(self):
    	return self.user.get_full_name()

# Types of workshops. These are defined in visit_stats_help.html
VISIT_TYPES_BASE = (
	(0, 'Robogals workshop, metro area'),
	(7, 'Robogals workshop, regional area'),
	(1, 'Robogals career talk'),
	(2, 'Robogals event'),
	(3, 'Non-Robogals workshop'),
	(4, 'Non-Robogals career talk'),
	(5, 'Non-Robogals event'),
	(6, 'Other'),
)

# Types of reports.
# This includes some special options like combining metro and regional figures.
VISIT_TYPES_REPORT = (
	(-2, 'Robogals workshops, sum of metro and regional'),
	(0, 'Robogals workshops, metro area'),
	(7, 'Robogals workshops, regional area'),
	(1, 'Robogals career talks'),
	(2, 'Robogals events'),
	(3, 'Non-Robogals workshops'),
	(4, 'Non-Robogals career talks'),
	(5, 'Non-Robogals events'),
	(6, 'Other'),
	(-1, 'Sum of all categories'),
)

# A set of statistics attached to a SchoolVisit (workshop) object.
# These stats are entered in when the SchoolVisit (workshop) is closed.
# There should be a maximum of one SchoolVisitStats object for each SchoolVisit object.
class SchoolVisitStats(models.Model):
	visit = models.ForeignKey(SchoolVisit, editable=False)
	visit_type = models.IntegerField(choices=VISIT_TYPES_BASE, null=False)
	primary_girls_first = models.PositiveSmallIntegerField(blank=True, null=True)
	primary_girls_repeat = models.PositiveSmallIntegerField(blank=True, null=True)
	primary_boys_first = models.PositiveSmallIntegerField(blank=True, null=True)
	primary_boys_repeat = models.PositiveSmallIntegerField(blank=True, null=True)
	high_girls_first = models.PositiveSmallIntegerField(blank=True, null=True)
	high_girls_repeat = models.PositiveSmallIntegerField(blank=True, null=True)
	high_boys_first = models.PositiveSmallIntegerField(blank=True, null=True)
	high_boys_repeat = models.PositiveSmallIntegerField(blank=True, null=True)
	other_girls_first = models.PositiveSmallIntegerField(blank=True, null=True)
	other_girls_repeat = models.PositiveSmallIntegerField(blank=True, null=True)
	other_boys_first = models.PositiveSmallIntegerField(blank=True, null=True)
	other_boys_repeat = models.PositiveSmallIntegerField(blank=True, null=True)
	notes = models.TextField("General notes", blank=True)

	# Add up the total number of girls taught at this workshop
	def num_girls(self):
		sum = 0
		if self.primary_girls_first:
			sum += self.primary_girls_first
		if self.primary_girls_repeat:
			sum += self.primary_girls_repeat
		if self.high_girls_first:
			sum += self.high_girls_first
		if self.high_girls_repeat:
			sum += self.high_girls_repeat
		if self.other_girls_first:
			sum += self.other_girls_first
		if self.other_girls_repeat:
			sum += self.other_girls_repeat
		return sum

	# Add up the total number of girls taught at this workshop,
	# with repeat visits given a 0.5 weighting
	def num_girls_weighted(self):
		sum = 0.0
		if self.primary_girls_first:
			sum += self.primary_girls_first
		if self.primary_girls_repeat:
			sum += (float(self.primary_girls_repeat) / 2)
		if self.high_girls_first:
			sum += self.high_girls_first
		if self.high_girls_repeat:
			sum += (float(self.high_girls_repeat) / 2)
		if self.other_girls_first:
			sum += self.other_girls_first
		if self.other_girls_repeat:
			sum += (float(self.other_girls_repeat) / 2)
		return sum

	# The chapter that ran this workshop
	def chapter(self):
		return self.visit.chapter

	def __unicode__(self):
		return str(self.num_girls()) + " at " + self.visit.__unicode__()

	class Meta:
		verbose_name = "workshop stats"
		verbose_name_plural = "workshop stats"
