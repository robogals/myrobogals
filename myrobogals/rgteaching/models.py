from django.db import models
from myrobogals.auth.models import Group, User
from datetime import datetime

class School(models.Model):
	name = models.CharField(max_length=64)
	chapter = models.ForeignKey(Group)
	address = models.TextField(blank=True)
	contact_person = models.CharField(max_length=64, blank=True)
	contact_position = models.CharField(max_length=64, blank=True)
	contact_email = models.CharField(max_length=64, blank=True)
	contact_phone = models.CharField(max_length=32, blank=True)
	notes = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.name

class Event(models.Model):
	STATUS_CHOICES = (
		(0, 'Open'),
		(1, 'Closed'),
		(2, 'Cancelled'),
	)
	
	ALLOW_RSVP_CHOICES = (
		(0, 'Allow anyone to RSVP'),
		(1, 'Only allow invitees to RSVP'),
		(2, 'Do not allow anyone to RSVP'),
	)

	chapter = models.ForeignKey(Group)
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
		return "Visit to " + str(self.school) + " by " + str(self.chapter) + " on " + str(self.visit_start.date())
	
	class Meta:
		ordering = ['-visit_start']

	
class EventMessage(models.Model):
	event = models.ForeignKey(Event)
	user = models.ForeignKey(User)
	date = models.CharField(max_length=50)
	message = models.TextField("RSVP Message")
	
	def asdate(self):
		return datetime.strptime(self.date, '%Y-%m-%d %H:%M')

class TrainingSession(Event):
	def __unicode__(self):
		return "Training session at " + self.location + " by " + str(self.chapter) + " on " + str(self.visit_start.date())

	class Meta:
		verbose_name = "training session"

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
    
    def __unicode__(self):
    	return self.user.get_full_name()

class SchoolVisitStats(models.Model):

	VISIT_TYPES = ( 
		(0, 'Robogals robotics teaching'),
		(1, 'Robogals career visit'),
		(2, 'Robogals event'),
		(3, 'Non-Robogals robotics teaching'),
		(4, 'Non-Robogals career visit'),
		(5, 'Non-Robogals event'),
		(6, 'Other (specify in notes below)'),
	)
	visit = models.ForeignKey(SchoolVisit, editable=False)
	visit_type = models.IntegerField(choices=VISIT_TYPES, null=False)
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
	notes = models.TextField("General Notes", blank=True)
