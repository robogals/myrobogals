from django.db import models
from myrobogals.auth.models import Group, User
from datetime import date

class PositionType(models.Model):
	description = models.CharField(max_length=64)
	chapter = models.ForeignKey(Group, null=True, blank=True)
	rank = models.IntegerField()

	def __unicode__(self):
		return self.description

	class Meta:
		verbose_name = "position type"
		ordering = ('rank',)

class Position(models.Model):
	user = models.ForeignKey(User)
	positionType = models.ForeignKey(PositionType)
	positionChapter = models.ForeignKey(Group)
	position_date_start = models.DateField(default=date.today)
	position_date_end = models.DateField(null=True, blank=True)

	def __unicode__(self):
		if (self.position_date_end):
			return self.positionType.description + ", " + self.positionChapter.name + " (" + self.position_date_start.strftime("%b %Y") + " - " + self.position_date_end.strftime("%b %Y") + ")"
		else:
			return self.positionType.description + ", " + self.positionChapter.name + " (" + self.position_date_start.strftime("%b %Y") + " - present)"

	class Meta:
		ordering = ('-position_date_end', '-position_date_start')

class UserList(models.Model):
	name = models.CharField(max_length=128)
	chapter = models.ForeignKey(Group)
	users = models.ManyToManyField(User)
	
	def __unicode__(self):
		return self.name
