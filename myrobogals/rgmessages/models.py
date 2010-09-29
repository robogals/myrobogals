from django.db import models
from django.forms import ModelForm
from myrobogals.auth.models import User, Group
import datetime

class EmailMessage(models.Model):
	STATUS_CODES_MSG = (
		(-1, 'Wait'),
		(0, 'Pending'),
		(1, 'Complete'),
	)

	subject = models.CharField("Subject", max_length=256)
	body = models.TextField("Message Body")
	from_name = models.CharField("From Name", max_length=64)
	from_address = models.EmailField("From Address")
	reply_address = models.CharField("Reply Address", max_length=64)
	sender = models.ForeignKey(User)
	status = models.IntegerField("Status Code", choices=STATUS_CODES_MSG, default=0)
	date = models.DateTimeField("Time Sent (in UTC)")
	html = models.BooleanField("HTML", blank=True)
	
	def status_description(self):
		return STATUS_CODES_MSG[self.status]
	
	def __unicode__(self):
		return self.subject

	def save(self, *args, **kwargs):
		if self.date == None:
			self.date = datetime.datetime.now()
		super(EmailMessage, self).save(*args, **kwargs)


class EmailRecipient(models.Model):
	STATUS_CODES_RECIPIENT = (
		(0, 'Pending'),
		(1, 'Sent'),
		(2, 'Bounced'),
		(3, 'No sender address'),
		(4, 'Invalid sender address'),
		(5, 'Invalid recipient address'),
		(6, 'Unknown error')
	)

	message = models.ForeignKey(EmailMessage)
	user = models.ForeignKey(User, null=True, blank=True)
	to_name = models.CharField("To Name", max_length=128, blank=True)
	to_address = models.EmailField("To Email")
	status = models.IntegerField("Status Code", choices=STATUS_CODES_RECIPIENT, default=0)

	def status_description(self):
		return STATUS_CODES_RECIPIENT[self.status]
	
	def __unicode__(self):
		return self.to_address

class Newsletter(models.Model):
	name = models.CharField(max_length=128)
	
	def __unicode__(self):
		return self.name

class NewsletterSubscriber(models.Model):
	email = models.CharField(max_length=128)
	newsletter = models.ForeignKey(Newsletter)
	first_name = models.CharField(max_length=128, blank=True)
	last_name = models.CharField(max_length=128, blank=True)
	subscribed_date = models.DateTimeField(default=datetime.datetime.now)
	unsubscribed_date = models.DateTimeField(blank=True, null=True)
	active = models.BooleanField(blank=True, default=True)

	def __unicode__(self):
		return self.email
