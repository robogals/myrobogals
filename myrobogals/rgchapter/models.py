from django.db import models

class DisplayColumn(models.Model):
	field_name = models.CharField(max_length=64)
	display_name_en = models.CharField(max_length=64)
	display_name_de = models.CharField(max_length=64, blank=True)
	order = models.IntegerField(default=10)
	
	def __unicode__(self):
		return self.field_name
	
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
