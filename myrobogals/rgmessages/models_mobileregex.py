from django.db import models

class MobileRegexCollection(models.Model):
	description = models.CharField(max_length=64)
	errmsg = models.CharField(max_length=128)
	
	def __unicode__(self):
		return self.description

class MobileRegex(models.Model):
	collection = models.ForeignKey(MobileRegexCollection)
	regex = models.CharField(max_length=200)
	description = models.CharField(max_length=64)
	strip_digits = models.SmallIntegerField(default=0)
	prepend_digits = models.CharField(max_length=16, blank=True)
	
	def __unicode__(self):
		return self.regex
	
	class Meta:
		verbose_name_plural = 'Mobile regexes'
