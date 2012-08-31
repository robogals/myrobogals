from django.db import models
from datetime import datetime
from myrobogals.auth.models import User
from myrobogals.rgchapter.models import ShirtSize

class Conference(models.Model):
	name = models.CharField(max_length=64)
	start_date = models.DateField()
	end_date = models.DateField()
	early_rsvp_close = models.DateField()
	rsvp_close = models.DateField()
	late_rsvp_close = models.DateField()
	details = models.TextField(blank=True)
	url = models.CharField(max_length=128)
	committee_year = models.IntegerField(default=0, help_text="The committee year for the purposes of the relevant question in the RSVP form. Put 0 to remove this question from the form.")

	def __unicode__(self):
		return self.name

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
		(0, '2011/2012 committee, now outgoing'),
		(1, '2011/2012 committee, continuing into 2012/2013 committee'),
		(2, 'Incoming into 2012/2013 committee'),
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
	parts_attending = models.ManyToManyField(ConferencePart)
	rsvp_time = models.DateTimeField(default=datetime.now())
	check_in = models.DateField(null=True, blank=True)
	check_out = models.DateField(null=True, blank=True)
	gender = models.IntegerField(choices=GENDERS, default=0)
	custom1 = models.BooleanField()
	custom2 = models.BooleanField()
	custom3 = models.BooleanField()
	custom4 = models.BooleanField()
	custom5 = models.BooleanField()

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
	date = models.DateField(default=datetime.now())
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
