# coding: utf-8

from django.db import models
from django.forms import ModelForm
from myrobogals.auth.models import User, Group
from myrobogals.rgmain.models import Country
from django.db.models.fields import PositiveIntegerField
import datetime
from pytz import utc
import re
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os.path

class MessagesSettings(models.Model):
	key = models.CharField('key', unique=True, max_length=255)
	value = models.CharField(max_length=255)

	def __unicode__(self):
		return self.key + ': ' + self.value

	class Meta:
		verbose_name = "setting"
		verbose_name_plural = "settings"
		ordering = ['key']

class EmailFile(models.Model):
	emailfile = models.FileField(upload_to='emailFileUpload')

	def __unicode__(self):
		return self.emailfile.name

	def filename(self):
		return os.path.basename(self.emailfile.name)

	def filesize(self):
		try:
			size = self.emailfile.size
		except:
			size = -1
		return size

class EmailMessage(models.Model):
	STATUS_CODES_MSG = (
		(-1, 'Wait'),
		(0, 'Pending'),
		(1, 'Complete'),
	)

	SCHEDULED_DATE_TYPES = (
		(1, 'Sender\'s timezone'),
		(2, 'Recipient\'s timezone'),
	)

	TYPE = (
		(0, 'Normal'),
		(1, 'Forum'),
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
	scheduled = models.BooleanField("Scheduled", blank=True)
	scheduled_date = models.DateTimeField("Scheduled date (as entered)", null=True, blank=True)
	scheduled_date_type = models.IntegerField("Scheduled date type", choices=SCHEDULED_DATE_TYPES, default=1)
	email_type = models.IntegerField("Email type", choices=TYPE, default=0)
	upload_files = models.ManyToManyField(EmailFile, related_name='emailmessage_upload_files')
	
	def status_description(self):
		for status_code in self.STATUS_CODES_MSG:
			if self.status == status_code[0]:
				return status_code[1]
		return 'Status unknown'

	def scheduled_date_type_description(self):
		for scheduled_type in self.SCHEDULED_DATE_TYPES:
			if self.scheduled_date_type == scheduled_type[0]:
				return scheduled_type[1]
		return 'Scheduled type unknown'
	
	def __unicode__(self):
		return self.subject

	def save(self, *args, **kwargs):
		if self.date == None:
			self.date = datetime.datetime.now()
		super(EmailMessage, self).save(*args, **kwargs)

@receiver(pre_delete, sender=EmailMessage)
def EmailMessage_delete(sender, instance, **kwargs):
	try:
		for f in instance.upload_files.all():
			f.emailfile.delete()
			f.delete()
	except:
		pass

class EmailRecipient(models.Model):
	STATUS_CODES_RECIPIENT = (
		(0, 'Pending'),
		(1, 'Sent'),
		(2, 'Bounced'),
		(3, 'No sender address'),
		(4, 'Invalid sender address'),
		(5, 'Invalid recipient address'),
		(6, 'Unknown error'),
		(7, 'Opened')
	)

	message = models.ForeignKey(EmailMessage)
	user = models.ForeignKey(User, null=True, blank=True)
	to_name = models.CharField("To Name", max_length=128, blank=True)
	to_address = models.EmailField("To Email")
	status = models.IntegerField("Status Code", choices=STATUS_CODES_RECIPIENT, default=0)
	scheduled_date = models.DateTimeField("Scheduled date (in UTC)", null=True, blank=True)

	def set_scheduled_date(self):
		if not self.message.scheduled:
			self.scheduled_date = datetime.datetime.utcnow()
		else:
			if self.message.scheduled_date_type == 1:
				# Use sender's timezone
				local_tz = self.message.sender.tz_obj()
			else:
				# Use recipient's timezone
				if self.user:
					local_tz = self.user.tz_obj()
				else:
					local_tz = utc
			scheduled_date_local = local_tz.localize(self.message.scheduled_date)
			scheduled_date_utc = scheduled_date_local.astimezone(utc)
			self.scheduled_date = scheduled_date_utc.replace(tzinfo=None)

	def status_description(self):
		for status_code in self.STATUS_CODES_RECIPIENT:
			if self.status == status_code[0]:
				return status_code[1]
		return 'Status unknown'
	
	def __unicode__(self):
		return self.to_address

	def save(self, *args, **kwargs):
		if self.scheduled_date == None:
			self.set_scheduled_date()
		super(EmailRecipient, self).save(*args, **kwargs)

class PositiveBigIntegerField(PositiveIntegerField):
	empty_strings_allowed = False
	
	def get_internal_type(self):
		return "PositiveBigIntegerField"
	
	def db_type(self, connection):
		return "bigint UNSIGNED"

def validate_sms_chars(text):
	matches = re.compile(u'^[a-z|A-Z|0-9|\\n|\\r|@|£|\$|¥|è|é|ù|ì|ò|Ç|Ø|ø|Å|å|Δ|Φ|Γ|Λ|Ω|Π|Ψ|Σ|Θ|Ξ|_|\^|{|}|\\\\|\[|~|\]|\||€|Æ|æ|ß|É| |!|"|#|¤|\%|&|\'|(|)|\*|\+|\,|\-|\.|\/|:|;|<|=|>|\?|¡|Ä|Ö|Ñ|Ü|§|¿|ä|ö|ñ|ü|à]+$').findall(text)
	if matches == []:
		return False
	else:
		return True

class SMSLengthException(Exception):
	def __init__(self, errmsg):
		self.errmsg = errmsg
	def __str__(self):
		return self.errmsg

class SMSMessage(models.Model):
	SMS_STATUS_CODES_MSG = (
		(-1, 'Wait'),
		(0, 'Pending'),
		(1, 'Complete'),
		(2, 'Error'),
		(3, 'Limits exceeded'),
	)
	
	SCHEDULED_DATE_TYPES = (
		(1, 'Sender\'s timezone'),
		(2, 'Recipient\'s timezone'),
	)

	TYPE = (
		(0, 'Normal'),
		(1, 'Mobile verification'),
	)

	body = models.TextField("Message body")
	senderid = models.CharField("Sender ID", max_length=32)
	sender = models.ForeignKey(User)
	chapter = models.ForeignKey(Group, null=True, blank=True)
	status = models.IntegerField("Status code", choices=SMS_STATUS_CODES_MSG, default=0)
	date = models.DateTimeField("Date set (in UTC)")
	unicode = models.BooleanField("Unicode", blank=True)
	split = models.IntegerField("Split", default=1)
	scheduled = models.BooleanField("Scheduled", blank=True, default=False)
	scheduled_date = models.DateTimeField("Scheduled date (as entered)", null=True, blank=True)
	scheduled_date_type = models.IntegerField("Scheduled date type", choices=SCHEDULED_DATE_TYPES, default=1)
	sms_type = models.IntegerField("SMS type", choices=TYPE, default=0)

	def validate(self):
		if validate_sms_chars(self.body):
			self.unicode = False
			extrachars = 0
			length = len(self.body)
			for i in range(length):
				if self.body[i] == '^':
					extrachars += 1
				elif self.body[i] == '{':
					extrachars += 1
				elif self.body[i] == '}':
					extrachars += 1
				elif self.body[i] == '\\':
					extrachars += 1
				elif self.body[i] == '[':
					extrachars += 1
				elif self.body[i] == '~':
					extrachars += 1
				elif self.body[i] == ']':
					extrachars += 1
				elif self.body[i] == '|':
					extrachars += 1
				elif self.body[i] == u'€':
					extrachars += 1
			smslength = length + extrachars
			if (smslength <= 160):
				self.split = 1;
			elif (smslength <= 1530):
				smslength += 152;
				smslength -= (smslength % 153);
				self.split = smslength / 153;
			else:
				raise SMSLengthException("Your message is too long. Please reduce your message to 1530 characters or less")
		else:
			self.unicode = True
			if len(self.body) < 5:
				raise SMSLengthException("Your message is too short. Please lengthen your message to be 5 characters or more")
			elif len(self.body) > 80:
				raise SMSLengthException("Your message is too long. Please reduce your message to be 80 characters or less, or do not use unicode characters (e.g. foreign alphabets)")
			self.split = 1
	
	def status_description(self):
		for status_code in self.SMS_STATUS_CODES_MSG:
			if self.status == status_code[0]:
				return status_code[1]
		return 'Status unknown'
		
	def scheduled_date_type_description(self):
		for scheduled_type in self.SCHEDULED_DATE_TYPES:
			if self.scheduled_date_type == scheduled_type[0]:
				return scheduled_type[1]
		return 'Scheduled type unknown'
	
	def credits_used(self):
		return self.smsrecipient_set.count() * self.split
	
	def __unicode__(self):
		return "SMS " + str(self.date)

	def save(self, *args, **kwargs):
		if self.date == None:
			self.date = datetime.datetime.now()
		super(SMSMessage, self).save(*args, **kwargs)
	
	class Meta:
		verbose_name = "SMS message"

class SMSRecipient(models.Model):
	SMS_GATEWAYS = (
		(0, 'Use default'),
		(1, 'SMSGlobal'),
	)

	SMS_STATUS_CODES_RECIPIENT = (
		(0, 'Pending'),
		(1, 'Processing'),
		(5, 'Unknown error'),
		(6, 'Cancelled'),
		(7, 'Number barred'),
		(9, 'Number invalid'),
		(10, 'SMS sent'),
		(11, 'SMS accepted by carrier'),
		(12, 'SMS delivered'),
		(13, 'SMS undeliverable'),
		(14, 'SMS expired'),
		(15, 'SMS deleted by carrier'),
		(16, 'SMS rejected by carrier'),
		(17, 'SMS in unknown state'),
		(18, 'Construction error'),
		(19, 'Limits exceeded'),
		(20, 'Temporary error at SMSC'),
		(21, 'Permanent error at SMSC'),
		(22, 'Request to SMSC timed out'),
	)
	
	SMS_ERROR_CODES = (
		(0, 'Unknown subscriber'),
		(10, 'Network time-out'),
		(100, 'Facility not supported'),
		(101, 'Unknown subscriber'),
		(102, 'Facility not provided'),
		(103, 'Call barred'),
		(104, 'Operation barred'),
		(105, 'SC congestion'),
		(106, 'Facility not supported'),
		(107, 'Absent subscriber'),
		(108, 'Delivery fail'),
		(109, 'Sc congestion'),
		(110, 'Protocol error'),
		(111, 'MS not equipped'),
		(112, 'Unknown SC'),
		(113, 'SC congestion'),
		(114, 'Illegal MS'),
		(115, 'MS not a subscriber'),
		(116, 'Error in MS'),
		(117, 'SMS lower layer not provisioned'),
		(118, 'System fail'),
		(512, 'Expired'),
		(513, 'Rejected'),
		(515, 'No route to destination'),
		(608, 'System error'),
		(610, 'Invalid source address'),
		(611, 'Invalid destination address'),
		(625, 'Unknown destination'),
	)

	message = models.ForeignKey(SMSMessage)
	user = models.ForeignKey(User, null=True, blank=True)
	to_number = models.CharField("To number", max_length=16)
	status = models.IntegerField("Status code", choices=SMS_STATUS_CODES_RECIPIENT, default=0)
	gateway = models.IntegerField("Gateway", choices=SMS_GATEWAYS, default=0)
	gateway_msg_id = PositiveBigIntegerField(verbose_name="Gateway message ID", default=0)
	gateway_err = models.IntegerField("Error code", choices=SMS_ERROR_CODES, default=0)
	scheduled_date = models.DateTimeField("Scheduled date (in UTC)", null=True, blank=True)

	def set_scheduled_date(self):
		if not self.message.scheduled:
			self.scheduled_date = datetime.datetime.utcnow()
		else:
			if self.message.scheduled_date_type == 1:
				# Use sender's timezone
				local_tz = self.message.sender.tz_obj()
			else:
				# Use recipient's timezone
				if self.user:
					local_tz = self.user.tz_obj()
				else:
					local_tz = utc
			scheduled_date_local = local_tz.localize(self.message.scheduled_date)
			scheduled_date_utc = scheduled_date_local.astimezone(utc)
			self.scheduled_date = scheduled_date_utc.replace(tzinfo=None)

	def gateway_description(self):
		for gateway in self.SMS_GATEWAYS:
			if self.gateway == gateway[0]:
				return gateway[1]
		return 'Gateway unknown'

	def status_description(self):
		if self.status == 11 or self.status == 13:
			return str(self.get_status_display()) + ": " + str(self.get_gateway_err_display())
		else:
			return str(self.get_status_display())
	
	def __unicode__(self):
		return self.status_description()

	def save(self, *args, **kwargs):
		if self.scheduled_date == None:
			self.set_scheduled_date()
		super(SMSRecipient, self).save(*args, **kwargs)

class Newsletter(models.Model):
	name = models.CharField(max_length=128)
	from_name = models.CharField(max_length=128)
	from_email = models.CharField(max_length=128)
	from_user = models.ForeignKey(User)
	confirm_email = models.TextField(blank=True)
	confirm_subject = models.CharField(max_length=128, blank=True)
	confirm_url = models.CharField(max_length=128, blank=True)
	confirm_from_name = models.CharField(max_length=128, blank=True)
	confirm_from_email = models.CharField(max_length=128, blank=True)
	confirm_from_user = models.ForeignKey(User, related_name="+")
	confirm_html = models.BooleanField(blank=True)
	
	def __unicode__(self):
		return self.name
	
	def get_most_recent(self):
		try:
			most_recent_issue = EmailMessage.objects.filter(sender=self.from_user).order_by('-date')[0]
		except KeyError:
			most_recent_issue = None
		return most_recent_issue

class SubscriberType(models.Model):
	description = models.CharField(max_length=128)
	order = models.IntegerField()
	public = models.BooleanField(blank=True, default=True)

	def __unicode__(self):
		return self.description

	class Meta:
		verbose_name = "subscriber type"
		ordering = ('order',)

class NewsletterSubscriber(models.Model):
	email = models.EmailField()
	newsletter = models.ForeignKey(Newsletter)
	first_name = models.CharField(max_length=128, blank=True)
	last_name = models.CharField(max_length=128, blank=True)
	company = models.CharField(max_length=128, blank=True)
	subscriber_type = models.ForeignKey(SubscriberType, blank=True, null=True)
	country = models.ForeignKey(Country, blank=True, null=True)
	details_verified = models.BooleanField(blank=True, default=True)
	subscribed_date = models.DateTimeField(default=datetime.datetime.now)
	unsubscribed_date = models.DateTimeField(blank=True, null=True)
	active = models.BooleanField(blank=True, default=True)

	def __unicode__(self):
		return self.email

class PendingNewsletterSubscriber(models.Model):
	email = models.CharField(max_length=128)
	uniqid = models.CharField(max_length=64)
	newsletter = models.ForeignKey(Newsletter)
	pending_since = models.DateTimeField(default=datetime.datetime.now)
	
	def __unicode__(self):
		return self.email
