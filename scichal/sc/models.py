from django.db import models
from scichal.reg.models import JosUsers

class Entrant(models.Model):
    name = models.CharField(max_length=128)
    age = models.IntegerField()
    mentor_name = models.CharField(max_length=128)
    mentor_phone = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    comment = models.CharField("How heard about us", max_length=128)
    mentor_relation = models.CharField(max_length=128)
    postal = models.CharField(max_length=128)
    school = models.CharField(max_length=128)
    username = models.CharField(max_length=128)
    user = models.ForeignKey(JosUsers, null=True, blank=True)
    
    def __unicode__(self):
    	return self.name

class EmailMessage(models.Model):
	subject = models.CharField("Subject", max_length=256)
	body = models.TextField("Message Body")
	from_name = models.CharField("From Name", max_length=64)
	from_address = models.EmailField("From Address")
	reply_address = models.CharField("Reply Address", max_length=64)
	html = models.BooleanField("HTML", blank=True)
	
	def __unicode__(self):
		return self.subject
