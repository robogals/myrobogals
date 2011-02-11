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
