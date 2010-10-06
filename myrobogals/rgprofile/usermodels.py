from django.db import models

class University(models.Model):
	name = models.CharField(max_length=64)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)
		verbose_name = "university"
		verbose_name_plural = "universities"

class Country(models.Model):
	code = models.CharField("ISO code", max_length=2, primary_key=True)
	country_name = models.CharField("Country", max_length=128)
	
	def __unicode__(self):
		return self.country_name
	
	class Meta:
		ordering = ('country_name', 'code')
		verbose_name_plural = 'countries'
