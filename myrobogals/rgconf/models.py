from django.db import models
from datetime import datetime
from myrobogals.rgprofile.models import User
from myrobogals.rgchapter.models import Chapter
from myrobogals.rgmain.models import Timezone
from myrobogals.rgchapter.models import ShirtSize
from pytz import utc
from django.utils import timezone

class Conference(models.Model):
	POLICY_CHOICES = (
		(0, 'Registration to auto-close at RSVP deadline'),
		(1, 'Registration to auto-close at late RSVP deadline'),
		(2, 'Registraion open indefinitely'),
		(3, 'Registration closed'),
		(4, 'Conference closed and hidden from list'),
	)
	
	CUSTOM_CHECKBOX_SETTINGS = (
		(0, 'Disabled'),
		(1, 'Enabled, for use by organisers'),
		(2, 'Enabled, user-settable (not implemented)'),
	)

	name = models.CharField(max_length=64)
	start_date = models.DateField()
	end_date = models.DateField()
	details = models.TextField(blank=True)
	url = models.CharField(max_length=128, help_text="URL to page with information")
	host = models.ForeignKey(Chapter, blank=True, null=True)
	committee_year = models.IntegerField(default=0, help_text="The committee year for the purposes of the relevant question in the RSVP form. Put 0 to remove this question from the form.")
	early_rsvp_close = models.DateTimeField(help_text="Time in UTC when benefits for registering early should close (not implemented)")
	rsvp_close = models.DateTimeField(help_text="Time in UTC when registration will close; set policy below. Publicly viewable.")
	late_rsvp_close = models.DateTimeField(help_text="Time in UTC when late registration will close; set policy below. Not publicly viewable, so can be used to silently allow late RSVPs.")
	timezone = models.ForeignKey(Timezone, help_text="Timezone of the place where the conference is taking place. Used for RSVP deadlines")
	timezone_desc = models.CharField(max_length=128, help_text="Description of timezone, e.g. 'Melbourne time' or 'Pacific Time'")
	policy = models.IntegerField(choices=POLICY_CHOICES, default=1)
	closed_msg = models.CharField(max_length=128, blank=True, help_text="Message to be shown when registration is closed", default="This form is now closed. To add/modify/remove RSVPs please email ______________")
	enable_invoicing = models.BooleanField(default=False)
	custom1_setting = models.IntegerField(choices=CUSTOM_CHECKBOX_SETTINGS, default=0)
	custom1_label = models.CharField(max_length=32, blank=True)
	custom2_setting = models.IntegerField(choices=CUSTOM_CHECKBOX_SETTINGS, default=0)
	custom2_label = models.CharField(max_length=32, blank=True)
	custom3_setting = models.IntegerField(choices=CUSTOM_CHECKBOX_SETTINGS, default=0)
	custom3_label = models.CharField(max_length=32, blank=True)
	custom4_setting = models.IntegerField(choices=CUSTOM_CHECKBOX_SETTINGS, default=0)
	custom4_label = models.CharField(max_length=32, blank=True)
	custom5_setting = models.IntegerField(choices=CUSTOM_CHECKBOX_SETTINGS, default=0)
	custom5_label = models.CharField(max_length=32, blank=True)

	def __unicode__(self):
		return self.name
	
	def is_open(self):
		if self.policy == 3:
			# Always closed
			return False
		elif self.policy == 4:
			# Closed and hidden
			return False
		elif self.policy == 2:
			# Always open
			return True
		elif self.policy == 0:
			# Closed after deadline
			if timezone.now() > self.rsvp_close:
				return False
			else:
				return True
		elif self.policy == 1:
			# Closed after late deadline
			if timezone.now() > self.late_rsvp_close:
				return False
			else:
				return True
		else:
			# Invalid policy type
			return False
	
	def is_hidden(self):
		if self.policy == 4:
			return True
		else:
			return False

	class Meta:
		ordering = ('-start_date',)

class ConferenceCurrency(models.Model):
	iso_code = models.CharField(max_length=3, verbose_name="ISO code")
	name = models.CharField(max_length=64)
	symbol = models.CharField(max_length=8)
	format = models.CharField(max_length=16)

	def __unicode__(self):
		return self.name
	
	def formatted(self, amount):
		return str(self.format) % amount

	class Meta:
		verbose_name = "currency"
		verbose_name_plural = "currencies"

class ConferencePart(models.Model):
	conference = models.ForeignKey(Conference)
	title = models.CharField(max_length=128)
	details = models.TextField(blank=True)
	cost = models.DecimalField(max_digits=9, decimal_places=2)
	gst_incl = models.BooleanField(default=True, verbose_name="GST included")
	currency = models.ForeignKey(ConferenceCurrency)
	order = models.IntegerField()

	def __unicode__(self):
		return self.title
	
	def cost_formatted(self):
		return str(self.currency.format) % self.cost

	class Meta:
		verbose_name = "part"
		ordering = ('conference', 'order')

class ConferenceAttendee(models.Model):
	ATTENDEE_TYPE_CHOICES = (
		(0, 'Outgoing from committee'),
		(1, 'Continuing in commmitee'),
		(2, 'Incoming into committee'),
		(3, 'None of the above; ordinary volunteer'),
	)
	
	GENDERS = (
		(0, 'Unknown'),
		(1, 'Male'),
		(2, 'Female'),
	)			
	
	conference = models.ForeignKey(Conference)
	user = models.ForeignKey(User)
	first_name = models.CharField(max_length=64)
	last_name = models.CharField(max_length=64)
	attendee_type = models.IntegerField(choices=ATTENDEE_TYPE_CHOICES, blank=True, null=True)
	outgoing_position = models.CharField(max_length=64, blank=True)
	incoming_position = models.CharField(max_length=64, blank=True)
	email = models.EmailField('E-mail address')
	mobile = models.CharField(max_length=32)
	dob = models.DateField()
	emergency_name = models.CharField(max_length=64)
	emergency_number = models.CharField(max_length=32)
	emergency_relationship = models.CharField(max_length=64)
	tshirt = models.ForeignKey(ShirtSize, null=True, blank=True)
	arrival_time = models.CharField(max_length=64, blank=True)
	dietary_reqs = models.CharField(max_length=64, blank=True)
	comments = models.CharField(max_length=128, blank=True)
	parts_attending = models.ManyToManyField(ConferencePart, blank=True, null=True)
	rsvp_time = models.DateTimeField(auto_now_add=True, help_text="Time in conference timezone when this person registered (does not change if RSVP edited)")
	check_in = models.DateField(null=True, blank=True)
	check_out = models.DateField(null=True, blank=True)
	gender = models.IntegerField(choices=GENDERS, default=0)
	custom1 = models.BooleanField(default=False)
	custom2 = models.BooleanField(default=False)
	custom3 = models.BooleanField(default=False)
	custom4 = models.BooleanField(default=False)
	custom5 = models.BooleanField(default=False)

	def get_position(self):
		if self.attendee_type == 0:
			if self.outgoing_position:
				return "Outgoing " + self.outgoing_position
			else:
				return ""
		elif self.attendee_type == 1 or self.attendee_type == 2:
			if self.incoming_position:
				return self.incoming_position
			else:
				return ""
		else:
			return ""

	def total_cost(self):
		sum = 0.0
		currency = None
		for part in self.parts_attending.all():
			sum += float(part.cost)
			if currency == None:
				currency = part.currency
			elif currency == part.currency:
				pass
			else:
				# Multiple currencies in the same conference; can't total
				return (0.0, None)
		return (sum, currency)
	
	def total_cost_formatted(self):
		sum, currency = self.total_cost()
		if currency != None:
			return currency.formatted(sum)
		else:
			return None
	
	def total_gst(self):
		sum = 0.0
		currency = None
		for part in self.parts_attending.all():
			if part.gst_incl:
				sum += float(part.cost)
				if currency == None:
					currency = part.currency
				elif currency == part.currency:
					pass
				else:
					# Multiple currencies in the same conference; can't total
					return (0.0, None)
		return ((sum / 11.0), currency)

	def total_gst_formatted(self):
		sum, currency = self.total_gst()
		if currency != None:
			return currency.formatted(sum)
		else:
			return None
	
	def payments_made(self):
		sum = 0.0
		currency = None
		for payment in self.conferencepayment_set.all():
			sum += float(payment.amount)
			if currency == None:
				currency = payment.currency
			elif currency == payment.currency:
				pass
			else:
				# Multiple currencies in the same conference; can't total
				return (0.0, None)
		return (sum, currency)

	def payments_made_formatted(self):
		sum, currency = self.payments_made()
		if currency != None:
			return currency.formatted(sum)
		else:
			return None
	
	def balance_owing(self):
		payment_sum, payment_currency = self.payments_made()
		cost_sum, cost_currency = self.total_cost()
		if payment_currency == None or payment_currency == cost_currency:
			return (cost_sum - payment_sum, cost_currency)
		else:
			# Cost and payment in different currencies
			return None

	def balance_owing_formatted(self):
		balance, currency = self.balance_owing()
		if currency != None:
			return currency.formatted(balance)
		else:
			return None
	
	def chapter(self):
		return self.user.chapter
	
	def full_name(self):
		return self.first_name + " " + self.last_name
	
	def __unicode__(self):
		return str(self.conference) + ": " + self.full_name()

	class Meta:
		ordering = ('conference', 'last_name', 'first_name')
		verbose_name = "attendee"

class ConferencePayment(models.Model):
	PAYMENT_METHOD_CHOICES = (
		(0, 'Other'),
		(1, 'Direct deposit'),
		(2, 'PayPal'),
		(3, 'Credit card'),
		(4, 'Cash'),
		(5, 'Cheque'),
		(6, 'Paid by Robogals'),
	)

	attendee = models.ForeignKey(ConferenceAttendee)
	date = models.DateField(auto_now_add=True)
	amount = models.DecimalField(max_digits=9, decimal_places=2)
	payment_method = models.IntegerField(choices=PAYMENT_METHOD_CHOICES, default=1)
	currency = models.ForeignKey(ConferenceCurrency)
	notes = models.TextField(blank=True)

	def __unicode__(self):
		return "Payment of " + self.amount_formatted() + " from " + str(self.attendee)

	def amount_formatted(self):
		return str(self.currency.format) % self.amount

	def attendee_name(self):
		return self.attendee.full_name()

	def conference(self):
		return self.attendee.conference

	class Meta:
		ordering = ('-date',)
		verbose_name = "payment"
