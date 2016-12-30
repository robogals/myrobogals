from myrobogals.rgprofile.models import User
from myrobogals.rgmain.models import Country
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient, NewsletterSubscriber, Newsletter, SubscriberType
from datetime import datetime, date
import re
from myrobogals.rgmain.utils import email_re
from django.db.models import Q

class RgImportCsvException(Exception):
	def __init__(self, errmsg):
		self.errmsg = errmsg
	def __str__(self):
		return self.errmsg

class SkipRowException(Exception):
	pass

def stringval(colname, cell, newuser, defaults):
	data = cell.strip()
	if data != "":
		setattr(newuser, colname, data)
	else:
		if colname in defaults:
			setattr(newuser, colname, defaults[colname])

def dateval(colname, cell, newuser, defaults):
	data = cell.strip()
	try:
		date = datetime.strptime(data)
		setattr(newuser, colname, date)
	except ValueError:
		if colname in defaults:
			setattr(newuser, colname, defaults[colname])

def numval(colname, cell, newuser, defaults, options):
	data = cell.strip()
	try:
		num = int(data)
		if num in options:
			setattr(newuser, colname, num)
		else:
			raise ValueError
	except ValueError:
		if colname in defaults:
			setattr(newuser, colname, defaults[colname])

def boolval(colname, cell, newuser, defaults):
	data = cell.strip().lower()
	if data != "":
		if data == 'true':
			setattr(newuser, colname, True)
		elif data == '1':
			setattr(newuser, colname, True)
		elif data == 'yes':
			setattr(newuser, colname, True)
		else:
			if colname in defaults:
				setattr(newuser, colname, defaults[colname])
	else:
		if colname in defaults:
			setattr(newuser, colname, defaults[colname])

def check_username(username):
	try:
		User.objects.get(username=username)
	except User.DoesNotExist:
		return True
	return False

def importcsv(filerows, welcomeemail, defaults, newsletter, user):
	columns = None
	subscribers_imported = 0
	most_recent_issue = newsletter.get_most_recent()
	if defaults['type']:
		defaults['subscriber_type_id'] = defaults['type'].pk
	countries = Country.objects.all()
	country_ids = []
	for country in countries:
		country_ids.append(country.pk)
	for row in filerows:
		try:
			# Get column names from first row
			if (columns == None):
				columns = row
				if 'email' not in columns:
					raise RgImportCsvException('You must specify an email field')
				continue
			
			# Create new user
			newsubscriber = NewsletterSubscriber()
			
			# Process row
			i = 0;
			send_most_recent = defaults['send_most_recent']
			send_email = False
			for cell in row:
				colname = columns[i]
				if colname == 'email':
					stringval(colname, cell, newsubscriber, defaults)
					if not email_re.match(newsubscriber.email):
						raise SkipRowException
					if NewsletterSubscriber.objects.filter(email=newsubscriber.email, newsletter=newsletter).count() > 0:
						raise SkipRowException   # This email address is already subscribed
					if newsletter.pk == 1:
						users_count = User.objects.filter(is_active=True, email=newsubscriber.email, email_newsletter_optin=True).count()
						if users_count > 0:
							raise SkipRowException   # This email address is already subscribed by having User.email_newsletter_optin True
					if newsletter.pk == 5:
						users_count = User.objects.filter(is_active=True, email=newsubscriber.email, email_careers_newsletter_AU_optin=True).count()
						if users_count > 0:
							raise SkipRowException   # This email address is already subscribed by having User.email_newsletter_optin True
				elif colname == 'first_name':
					stringval(colname, cell, newsubscriber, defaults)
				elif colname == 'last_name':
					stringval(colname, cell, newsubscriber, defaults)
				elif colname == 'company':
					stringval(colname, cell, newsubscriber, defaults)
				elif colname == 'type':
					types = SubscriberType.objects.all()
					type_ids = []
					for type in types:
						type_ids.append(type.pk)
					numval('subscriber_type_id', cell, newsubscriber, defaults, type_ids)
				elif colname == 'country':
					if cell in country_ids:
						stringval('country_id', cell, newsubscriber, defaults)
					else:
						newsubscriber.country = defaults['country']
				elif colname == 'details_verified':
					boolval(colname, cell, newsubscriber, defaults)
				elif colname == 'send_most_recent':
					data = cell.strip()
					if data == 'true':
						send_most_recent = True
					elif data == '1':
						send_most_recent = True
					elif data == 'yes':
						send_most_recent = True
					if data == 'false':
						send_most_recent = False
					elif data == '0':
						send_most_recent = False
					elif data == 'no':
						send_most_recent = False
				elif colname == 'send_email':
					data = cell.strip()
					if data == 'true':
						send_email = True
					elif data == '1':
						send_email = True
					elif data == 'yes':
						send_email = True
				else:
					pass   # Unknown column, ignore
				# Increment column and do the loop again
				i += 1
	
			# Apply any unapplied defaults
			if 'type' not in columns:
				if 'subscriber_type_id' in defaults:
					newsubscriber.subscriber_type_id = defaults['subscriber_type_id']
			if 'details_verified' not in columns:
				if 'details_verified' in defaults:
					newsubscriber.details_verified = defaults['details_verified']
			if 'country' not in columns:
				if 'country' in defaults:
					newsubscriber.country = defaults['country']
	
			# Set some other important attributes
			newsubscriber.newsletter = newsletter
			newsubscriber.subscribed_date = datetime.now()
			newsubscriber.active = True
	
			# And finally...
			newsubscriber.save()
	
			# Send welcome email, if applicable
			if (welcomeemail['importaction'] == '1' or (welcomeemail['importaction'] == '3' and send_email)):
				message = EmailMessage()
				message.subject = welcomeemail['subject']
				try:
					message.body = welcomeemail['body'].format(
						newsletter=newsletter,
						subscriber=newsubscriber)
				except Exception:
					newsubscriber.delete()
					raise RgImportCsvException('Welcome email format is invalid')
				message.from_address = welcomeemail['from_address']
				message.reply_address = welcomeemail['reply_address']
				message.from_name = welcomeemail['from_name']
				message.sender = user
				message.html = welcomeemail['html']
				message.status = -1
				message.save()
				recipient = EmailRecipient()
				recipient.message = message
				recipient.to_name = newsubscriber.first_name + " " + newsubscriber.last_name
				recipient.to_address = newsubscriber.email
				recipient.save()
				message.status = 0
				message.save()
			
			# Send most recent newsletter, if applicable
			if send_most_recent:
				recipient = EmailRecipient()
				recipient.message = most_recent_issue
				recipient.to_name = newsubscriber.first_name + " " + newsubscriber.last_name
				recipient.to_address = newsubscriber.email
				recipient.save()
	
			# Increment counter
			subscribers_imported += 1
		except SkipRowException:
			continue   # Skip this row

	# Tell the most recent issue to send with new subscribers,
	# if applicable
	most_recent_issue.status = 0
	most_recent_issue.save()
	return subscribers_imported

def genandsendpw(user, welcomeemail, chapter):
	plaintext_password = User.objects.make_random_password(6)
	user.set_password(plaintext_password)
	user.save()
	
	message = EmailMessage()
	message.subject = welcomeemail['subject']
	try:
		message.body = welcomeemail['body'].format(
			chapter=chapter,
			user=user,
			plaintext_password=plaintext_password)
	except Exception:
		raise RgGenAndSendPwException('Email body contains invalid fields')
	message.from_address = 'my@robogals.org'
	message.reply_address = 'my@robogals.org'
	message.from_name = chapter.name
	message.sender = User.objects.get(username='edit')
	message.html = welcomeemail['html']
	message.status = -1
	message.save()
	recipient = EmailRecipient()
	recipient.message = message
	recipient.user = user
	recipient.to_name = user.get_full_name()
	recipient.to_address = user.email
	recipient.save()
	message.status = 0
	message.save()

def importFromAmplifierToAUcareer():
	country = Country.objects.get(code="AU")
	amplifier = Newsletter.objects.get(pk=1)
	career = Newsletter.objects.get(pk=5)
	for user in User.objects.filter(chapter__country=country, email_newsletter_optin=True):
		user.email_careers_newsletter_AU_optin = True
		user.save()
	for subscriber in NewsletterSubscriber.objects.filter(newsletter=amplifier, active=True):
		if NewsletterSubscriber.objects.filter(email=subscriber.email, newsletter=career).count() > 0:
			continue	# This email address is already subscribed
		users_count = User.objects.filter(is_active=True, email=subscriber.email, email_careers_newsletter_AU_optin=True).count()
		if users_count > 0:
			continue    # This email address is already subscribed by having User.email_careers_newsletter_AU_optin True
		subscriber.id = None
		subscriber.newsletter = career
		subscriber.save()
