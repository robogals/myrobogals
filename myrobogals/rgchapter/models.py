from django.db import models
from django.utils import translation

class DisplayColumn(models.Model):
	field_name = models.CharField(max_length=64)
	display_name_en = models.CharField(max_length=64)
	display_name_nl = models.CharField(max_length=64, blank=True)
	display_name_ja = models.CharField(max_length=64, blank=True)
	order = models.IntegerField(default=10)
	
	def __unicode__(self):
		return self.field_name
	
	def display_name_local(self):
		print "display_name_" + translation.get_language()
		return getattr(self, "display_name_" + translation.get_language())
	
	class Meta:
		ordering = ('order','field_name')
		verbose_name = "Column display name"

class ShirtSize(models.Model):
	size_short = models.CharField(max_length=32)
	size_long = models.CharField(max_length=64)
	chapter = models.ForeignKey('auth.Group')
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
	award_description = models.CharField(max_length= 128)
	
	def __unicode__(self):
		return self.award_name
		
	class Meta:
		ordering = ('award_type', 'award_name')
		verbose_name = "Award"
		
REGION_CHOICES = (
	(0, 'Australia & New Zealand'),
	(1, 'UK & Europe')
)

class AwardRecipient(models.Model):

	award = models.ForeignKey(Award)
	chapter = models.ForeignKey('auth.Group')
	year = models.IntegerField(default=2000)
	region = models.IntegerField(choices=REGION_CHOICES, default=0)
	description = models.CharField(max_length=128)
	
	def __unicode__(self):
		return self.award.award_name
		
	class Meta:
		ordering = ('-year', 'award', 'region', 'chapter')
		verbose_name = "Award recipient"