# coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from myrobogals.auth.models import User, Group, MemberStatusType
from myrobogals.rgmessages.models import SMSMessage, SMSRecipient, EmailMessage, EmailRecipient, Newsletter, NewsletterSubscriber, PendingNewsletterSubscriber, SubscriberType, SMSLengthException
from myrobogals.rgprofile.models import UserList
from myrobogals.admin.widgets import FilteredSelectMultiple
from myrobogals.settings import API_SECRET, SECRET_KEY, MEDIA_ROOT
from django.core.validators import email_re
from hashlib import md5
from urllib import unquote_plus
from datetime import datetime, date
from tinymce.widgets import TinyMCE
from myrobogals.rgmain.models import Country
from django.utils.translation import ugettext_lazy as _
from myrobogals.auth.decorators import login_required
from time import time
from myrobogals.rgmessages.functions import importcsv, RgImportCsvException
import csv
from myrobogals.rgmain.utils import SelectDateWidget, SelectTimeWidget
from pytz import utc
from decimal import *
from operator import itemgetter


class EmailModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.last_name + ", " + obj.first_name
        #return obj.last_name + ", " + obj.first_name + " (" + obj.email + ")"

class WriteEmailForm(forms.Form):
	SCHEDULED_DATE_TYPES = (
		(1, 'My timezone'),
		(2, 'Recipients\' timezones'),
	)

	subject = forms.CharField(max_length=256)
	body = forms.CharField(widget=TinyMCE(attrs={'cols': 70}))
	from_type = forms.ChoiceField(choices=((0,"Robogals"),(1,_("Chapter name")),(2,_("Your name"))), initial=1)
	recipients = EmailModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple(_("Recipients"), False, attrs={'rows': 10}), required=False)
	chapters = forms.ModelMultipleChoiceField(queryset=Group.objects.all().order_by('name'), widget=FilteredSelectMultiple(_("Chapters"), False, attrs={'rows': 10}), required=False)
	chapters_exec = forms.ModelMultipleChoiceField(queryset=Group.objects.all().order_by('name'), widget=FilteredSelectMultiple(_("Chapters"), False, attrs={'rows': 10}), required=False)
	list = forms.ModelChoiceField(queryset=UserList.objects.none(), required=False)
	newsletters = forms.ModelChoiceField(queryset=Newsletter.objects.all(), required=False)
	schedule_time = forms.TimeField(widget=SelectTimeWidget(), initial=datetime.now(), required=False)
	schedule_date = forms.DateField(widget=SelectDateWidget(years=range(datetime.now().year, datetime.now().year + 2)), initial=datetime.now(), required=False)
	schedule_zone = forms.ChoiceField(choices=SCHEDULED_DATE_TYPES, initial=2, required=False)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		super(WriteEmailForm, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['recipients'].queryset = User.objects.filter(is_active=True, email_chapter_optin=True).exclude(email='').order_by('last_name')
		else:
			self.fields['recipients'].queryset = User.objects.filter(chapter=user.chapter, is_active=True, email_chapter_optin=True).exclude(email='').order_by('last_name')
		self.fields['list'].queryset = UserList.objects.filter(chapter=user.chapter)
		self.fields['from_type'].choices = (
			(0, "Robogals <" + user.email + ">"),
			(1, user.chapter.name + " <" + user.email + ">"),
			(2, user.get_full_name() + " <" + user.email + ">")
		)
		self.fields['list'].queryset = UserList.objects.filter(chapter=user.chapter)
		self.fields['schedule_time'].initial = utc.localize(datetime.now()).astimezone(user.tz_obj())
		self.fields['schedule_date'].initial = utc.localize(datetime.now()).astimezone(user.tz_obj())

@login_required
def writeemail(request):
	memberstatustypes = MemberStatusType.objects.all()
	if not request.user.is_staff:
		raise Http404
	if request.method == 'POST':
		typesel = request.POST['type']
		schedsel = request.POST['scheduling']
		statussel = request.POST['status']
		
		if 'step' in request.POST:
			if request.POST['step'] == '1':
				emailform = WriteEmailForm(request.POST, user=request.user)
				request.session['emailform'] = emailform
			elif request.POST['step'] == '2':
				if 'emailform' not in request.session:
					raise Http404
				emailform = request.session['emailform']
				del request.session['emailform']
			else:
				raise Http404
		else:
			raise Http404
		if emailform.is_valid():
			data = emailform.cleaned_data
			if request.POST['step'] == '2':
				message = EmailMessage()
				message.subject = data['subject']
				message.body = data['body']
				message.from_address = request.user.email
				message.reply_address = request.user.email
				message.sender = request.user
				message.html = True

				if request.POST['scheduling'] == '1':
					message.scheduled = True
					message.scheduled_date = datetime.combine(data['schedule_date'], data['schedule_time'])
					try:
						message.scheduled_date_type = int(data['schedule_zone'])
					except Exception:
						message.scheduled_date_type = 1
				else:
					message.scheduled = False

				if request.POST['type'] == '4':
					n = data['newsletters']
					message.from_name = n.from_name
					message.from_address = n.from_email
					message.reply_address = n.from_email
					message.sender = n.from_user
				else:
					message.content_subtype = "html"
					if int(data['from_type']) == 0:
						message.from_name = "Robogals"
					elif int(data['from_type']) == 1:
						message.from_name = request.user.chapter.name
					else:
						message.from_name = request.user.get_full_name()
					
				# Don't send it yet until the recipient list is done
				message.status = -1
				# Save to database so we get a value for the primary key,
				# which we need for entering the recipient entries
				message.save()

			if request.POST['type'] == '1':
				if request.user.is_superuser:
					# "Email all members worldwide" feature disabled Nov 2010 - too much potential for abuse.
					# Can be re-enabled by uncommenting the following line, commenting the exception,
					# and removing the disabled tag from the relevant radio button in email_write.html
					#users = User.objects.filter(chapter__in=data['chapters'], is_active=True, email_chapter_optin=True)
					raise Exception
				else:
					users = User.objects.filter(chapter=request.user.chapter, is_active=True, email_chapter_optin=True).exclude(email='')
			elif request.POST['type'] == '2':
				if request.user.is_superuser:
					users = User.objects.filter(chapter__in=data['chapters_exec'], is_active=True, is_staff=True).exclude(email='')
				else:
					users = User.objects.filter(chapter=request.user.chapter, is_active=True, is_staff=True).exclude(email='')
			elif request.POST['type'] == '5':
				ul = data['list']
				users = ul.users.all().exclude(email='')
			elif request.POST['type'] == '4':
				if request.user.is_superuser:
					# Special rule for The Amplifier
					if data['newsletters'].pk == 1:
						users = User.objects.filter(is_active=True, email_newsletter_optin=True).exclude(email='')
					else:
						users = User.objects.none()
			else:
				users = data['recipients']

			usersfiltered = []
			if statussel != '0' and request.POST['type'] != '4':
				for one_user in users:
					if((one_user.memberstatus_set.get(status_date_end__isnull=True)).statusType == MemberStatusType.objects.get(pk=(int(statussel)))):
						if request.POST['step'] == '1':
							usersfiltered.append(one_user)
						else:
							if str(one_user.pk) in request.POST.keys():
								recipient = EmailRecipient()
								recipient.message = message
								recipient.user = one_user
								recipient.to_name = one_user.get_full_name()
								recipient.to_address = one_user.email
								recipient.save()
			else:
				for one_user in users:
					if request.POST['step'] == '1':
						usersfiltered.append(one_user)
					else:
						if str(one_user.pk) in request.POST.keys():
							recipient = EmailRecipient()
							recipient.message = message
							recipient.user = one_user
							recipient.to_name = one_user.get_full_name()
							recipient.to_address = one_user.email
							recipient.save()
			
			subscribers = []
			if request.POST['type'] == '4' and request.user.is_superuser:
				for one_subscriber in NewsletterSubscriber.objects.filter(newsletter=data['newsletters'], active=True):
					if request.POST['step'] == '1':
						subscribers.append(one_subscriber)
					else:
						if ('sub' + str(one_subscriber.pk)) in request.POST.keys():
							recipient = EmailRecipient()
							recipient.message = message
							recipient.user = None
							recipient.to_name = one_subscriber.first_name + " " + one_subscriber.last_name
							recipient.to_address = one_subscriber.email
							recipient.save()
			
			if request.POST['step'] == '2':
				# Now mark it as OK to send. The email and all recipients are now in MySQL.
				# A background script on the server will process the queue.
				message.status = 0
				message.save()
			
			if request.POST['step'] == '1':
				return render_to_response('email_users_confirm.html', {'usersfiltered': usersfiltered, 'subscribers': subscribers, 'type': request.POST['type'], 'scheduling': request.POST['scheduling'], 'status': request.POST['status']}, context_instance=RequestContext(request))
			else:
				return HttpResponseRedirect('/messages/email/done/')
	else:
		if request.user.is_superuser:
			typesel = '2'
		else:
			typesel = '1'
		schedsel = '0'
		statussel = '1'
		emailform = WriteEmailForm(None, user=request.user)
	return render_to_response('email_write.html', {'memberstatustypes': memberstatustypes, 'emailform': emailform, 'chapter': request.user.chapter, 'typesel': typesel, 'schedsel': schedsel, 'statussel': statussel}, context_instance=RequestContext(request))

class SMSModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.last_name + ", " + obj.first_name + " (+" + obj.mobile + ")"

class WriteSMSForm(forms.Form):
	SCHEDULED_DATE_TYPES = (
		(1, 'My timezone'),
		(2, 'Recipients\' timezones'),
	)

	body = forms.CharField(widget=forms.Textarea(attrs={'cols': '35', 'rows': '7', 'onkeyup': 'updateTextBoxCounter();'}), initial=_("Put your message here.  To opt-out reply 'stop'"))
	from_type = forms.ChoiceField(choices=((0,"+61429558100 (myRobogals)"),), help_text=_('You can send SMSes from your own number if you <a href="%s">verify your number</a>') % '/profile/mobverify/')
	recipients = SMSModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple("Recipients", False, attrs={'rows': 10}), required=False)
	chapters = forms.ModelMultipleChoiceField(queryset=Group.objects.all().order_by('name'), widget=FilteredSelectMultiple("Chapters", False, attrs={'rows': 10}), required=False)
	chapters_exec = forms.ModelMultipleChoiceField(queryset=Group.objects.all().order_by('name'), widget=FilteredSelectMultiple("Chapters", False, attrs={'rows': 10}), required=False)
	list = forms.ModelChoiceField(queryset=UserList.objects.none(), required=False)
	schedule_time = forms.TimeField(widget=SelectTimeWidget(), initial=datetime.now(), required=False)
	schedule_date = forms.DateField(widget=SelectDateWidget(years=range(datetime.now().year, datetime.now().year + 2)), initial=datetime.now(), required=False)
	schedule_zone = forms.ChoiceField(choices=SCHEDULED_DATE_TYPES, initial=2, required=False)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		super(WriteSMSForm, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['recipients'].queryset = User.objects.filter(is_active=True, mobile_marketing_optin=True).exclude(mobile='').order_by('last_name')
		else:
			self.fields['recipients'].queryset = User.objects.filter(chapter=user.chapter, is_active=True, mobile_marketing_optin=True).exclude(mobile='').order_by('last_name')
		self.fields['list'].queryset = UserList.objects.filter(chapter=user.chapter)
		if user.mobile_verified:
			self.fields['from_type'].choices = (
				(1, "+" + user.mobile + " (you)"),
				(0,"+61429558100 (myRobogals)"),
			)
			self.fields['from_type'].initial = 1
			self.fields['from_type'].help_text = ''
		self.fields['schedule_time'].initial = utc.localize(datetime.now()).astimezone(user.tz_obj())
		self.fields['schedule_date'].initial = utc.localize(datetime.now()).astimezone(user.tz_obj())

@login_required
def writesms(request):
	memberstatustypes = MemberStatusType.objects.all()
	if not request.user.is_staff:
		raise Http404
	smserror = None
	if request.method == 'POST':
		typesel = request.POST['type']
		schedsel = request.POST['scheduling']
		statussel = request.POST['status']
		smsform = WriteSMSForm(request.POST, user=request.user)
		try:
			if smsform.is_valid():
				data = smsform.cleaned_data
				message = SMSMessage()
				message.body = data['body']
				message.sender = request.user
				message.chapter = request.user.chapter
				if int(data['from_type']) == 1 and request.user.mobile_verified:
					message.senderid = str(request.user.mobile)
				else:
					message.senderid = '61429558100'
				if request.POST['scheduling'] == '1':
					message.scheduled = True
					message.scheduled_date = datetime.combine(data['schedule_date'], data['schedule_time'])
					try:
						message.scheduled_date_type = int(data['schedule_zone'])
					except Exception:
						message.scheduled_date_type = 1
				else:
					message.scheduled = False
			
				# Validate, and calculate the values for unicode and split.
				# If the message is too long, the exception will be caught below.
				message.validate()
			
				# Don't send it yet until the recipient list is done
				message.status = -1
				# Save to database so we get a value for the primary key,
				# which we need for entering the recipient entries
				message.save()

				if request.POST['type'] == '1':
					if request.user.is_superuser:
					# "SMS all members worldwide" feature disabled - too much potential for abuse.
					# Can be re-enabled by uncommenting the following line, commenting the exception,
					# and removing the disabled tag from the relevant radio button in email_write.html
					#users = User.objects.filter(chapter__in=data['chapters'], is_active=True, email_chapter_optin=True)
						raise Exception
					else:
						users = User.objects.filter(chapter=request.user.chapter, is_active=True, mobile_marketing_optin=True).exclude(mobile='')
				elif request.POST['type'] == '2':
					if request.user.is_superuser:
						users = User.objects.filter(chapter__in=data['chapters_exec'], is_active=True, is_staff=True).exclude(mobile='')
					else:
						users = 	User.objects.filter(chapter=request.user.chapter, is_active=True, is_staff=True).exclude(mobile='')
				elif request.POST['type'] == '5':
					ul = data['list']
					users = ul.users.all().exclude(mobile='')
				else:
					# The form has already validated this to exclude
					# those users with a blank mobile number
					users = data['recipients']

				if statussel != '0':
					for one_user in users:
						if((one_user.memberstatus_set.get(status_date_end__isnull=True)).statusType == MemberStatusType.objects.get(pk=(int(statussel)))):
							recipient = SMSRecipient()
							recipient.message = message
							recipient.user = one_user
							recipient.to_number = one_user.mobile
							recipient.save()
				else:
					for one_user in users:
						recipient = SMSRecipient()
						recipient.message = message
						recipient.user = one_user
						recipient.to_number = one_user.mobile
						recipient.save()
			
				# Check that we haven't used too many credits
				sms_this_month = 0
				sms_this_month_obj = SMSMessage.objects.filter(date__gte=datetime(datetime.now().year, datetime.now().month, 1, 0, 0, 0), status__in=[0, 1])
				for obj in sms_this_month_obj:
					sms_this_month += obj.credits_used()
				sms_this_month += message.credits_used()
				if sms_this_month > request.user.chapter.sms_limit:
					message.status = 3
					message.save()
					return HttpResponseRedirect('/messages/sms/overlimit/')
			
				# Now mark it as OK to send. The email and all recipients are now in MySQL.
				# A background script on the server will process the queue.
				message.status = 0
				message.save()
			
				return HttpResponseRedirect('/messages/sms/done/')
		except SMSLengthException as e:
			smserror = e.errmsg
	else:
		if request.user.is_superuser:
			typesel = '2'
		else:
			typesel = '1'
		schedsel = '0'
		statussel = '1'
		smsform = WriteSMSForm(None, user=request.user)
	return render_to_response('sms_write.html', {'memberstatustypes': memberstatustypes, 'smsform': smsform, 'smserror': smserror, 'chapter': request.user.chapter, 'typesel': typesel, 'schedsel': schedsel, 'statussel': statussel}, context_instance=RequestContext(request))

@login_required
def smsdone(request):
	if not request.user.is_staff:
		raise Http404
	return render_to_response('sms_done.html', None, context_instance=RequestContext(request))

@login_required
def smsoverlimit(request):
	if not request.user.is_staff:
		raise Http404
	return render_to_response('sms_overlimit.html', {'chapter': request.user.chapter}, context_instance=RequestContext(request))

def serveimg(request, msgid, filename):
	try:
		recipient = EmailRecipient.objects.get(pk=msgid)
	except EmailRecipient.DoesNotExist:
		raise Http404
	recipient.status = 7
	recipient.save()
	try:
		image_data = open(MEDIA_ROOT + '/images/' + filename, "rb").read()
	except Exception:
		raise Http404
	return HttpResponse(image_data, mimetype="image/jpeg")
	
def servenewsletter(request, msgid, issue):
	try:
		recipient = EmailRecipient.objects.get(pk=msgid)
	except EmailRecipient.DoesNotExist:
		raise Http404
	recipient.status = 7
	recipient.save()
	return HttpResponseRedirect("http://www.robogals.org/amp-img/%s.html"%(issue))


@login_required
def emaildone(request):
	if not request.user.is_staff:
		raise Http404
	return render_to_response('email_done.html', None, context_instance=RequestContext(request))

@login_required
def smsrecipients(request, sms_id):
	sms = get_object_or_404(SMSMessage, pk=sms_id)
	if (sms.sender != request.user):
		raise Http404
	recipients = SMSRecipient.objects.filter(message=sms).order_by('user__chapter')
	return render_to_response('message_recipients.html', {'chapter': request.user.chapter, 'msgtype': 'sms', 'sms': sms, 'recipients': recipients}, context_instance=RequestContext(request))

@login_required
def emailrecipients(request, email_id):
	email = get_object_or_404(EmailMessage, pk=email_id)
	if (email.sender != request.user) or (email.email_type != 0):
		raise Http404
	recipients = EmailRecipient.objects.filter(message=email).order_by('user__chapter')
	return render_to_response('message_recipients.html', {'chapter': request.user.chapter, 'msgtype': 'email', 'email': email, 'recipients': recipients}, context_instance=RequestContext(request))

@login_required
def showemail(request, email_id):
	email = get_object_or_404(EmailMessage, pk=email_id)
	if (email.sender != request.user) and (not EmailRecipient.objects.filter(user=request.user, message=email)):
		raise Http404
	if email.email_type != 0:
		raise Http404
	return render_to_response('email_show.html', {'chapter': request.user.chapter, 'email': email}, context_instance=RequestContext(request))

@login_required
def msghistory(request):
	emailMsgsSent = EmailMessage.objects.filter(sender=request.user, email_type=0).order_by('-date')
	SMSMsgsSent = SMSMessage.objects.filter(sender=request.user, sms_type=0).order_by('-date')
	emailMsgsReceived = EmailRecipient.objects.filter(user=request.user, message__email_type=0).order_by('-scheduled_date')
	SMSMsgsReceived = SMSRecipient.objects.filter(user=request.user, message__sms_type=0).order_by('-scheduled_date')
	return render_to_response('message_history.html', {'chapter': request.user.chapter, 'emailMsgsSent': emailMsgsSent, 'SMSMsgsSent': SMSMsgsSent, 'emailMsgsReceived': emailMsgsReceived, 'SMSMsgsReceived': SMSMsgsReceived}, context_instance=RequestContext(request))

def api(request):
	if 'api' not in request.GET:
		return HttpResponse("-1")
	elif request.GET['api'] != API_SECRET:
		return HttpResponse("-1")
	elif 'action' in request.GET:
		try:
			n = Newsletter.objects.get(pk=request.GET['newsletter'])
		except Newsletter.DoesNotExist:
			return HttpResponse("-1")
		try:
			if request.GET['action'] == 'subscribe':
				email = unquote_plus(request.GET['email']).strip()
				if not email_re.match(email):
					return HttpResponse("C")  # Invalid email
				c = NewsletterSubscriber.objects.filter(email=email, newsletter=n, active=True).count()
				if c != 0:
					return HttpResponse("B")  # Already subscribed
				if n.pk == 1:
					users_count = User.objects.filter(is_active=True, email=email, email_newsletter_optin=True).count()
					if users_count > 0:
						return HttpResponse("B")  # Already subscribed
				try:
					# They've tried to subscribe already, so resend confirmation email
					p = PendingNewsletterSubscriber.objects.get(email=email, newsletter=n)
				except PendingNewsletterSubscriber.DoesNotExist:
					p = PendingNewsletterSubscriber()
					p.email = email
					p.uniqid = md5(SECRET_KEY + email + n.name).hexdigest()
					p.newsletter = n
					p.save()
				confirm_url = n.confirm_url + "pid=" + str(p.pk) + "&key=" + p.uniqid
				message = EmailMessage()
				message.subject = n.confirm_subject
				message.body = n.confirm_email.replace('{email}', email).replace('{url}', confirm_url)
				message.from_address = n.confirm_from_email
				message.from_name = n.confirm_from_name
				message.reply_address = n.confirm_from_email
				message.sender = n.confirm_from_user
				message.html = n.confirm_html
				# Don't send it yet until the recipient list is done
				message.status = -1
				# Save to database so we get a value for the primary key,
				# which we need for entering the recipient entries
				message.save()
				recipient = EmailRecipient()
				recipient.message = message
				recipient.to_name = ""
				recipient.to_address = email
				recipient.save()
				message.status = 0
				message.save()
				return HttpResponse("A")  # Success!
			elif request.GET['action'] == 'confirm':
				pid = unquote_plus(request.GET['id'])
				key = unquote_plus(request.GET['key'])
				try:
					p = PendingNewsletterSubscriber.objects.get(pk=pid, newsletter=n, uniqid=key)
				except PendingNewsletterSubscriber.DoesNotExist:
					return HttpResponse("B")
				try:
					if n.pk != 1:
						# Only do the user thing for The Amplifier (id = 1)
						raise User.DoesNotExist
					try:
						u = User.objects.get(email=p.email)
					except User.MultipleObjectsReturned:
						# Subscribe the first user with this email address
						u = User.objects.filter(email=p.email)[0]
					# This user is already a Robogals member
					u.email_newsletter_optin = True
					u.save()
				except User.DoesNotExist:
					ns = NewsletterSubscriber()
					ns.newsletter = n
					ns.email = p.email
					ns.active = True
					ns.details_verified = False
					ns.save()
				p.delete()
				return HttpResponse("A")
			elif request.GET['action'] == 'unsubscribe':
				email = unquote_plus(request.GET['email']).strip()
				try:
					ns = NewsletterSubscriber.objects.get(email=email, newsletter=n, active=True)
				except NewsletterSubscriber.DoesNotExist:
					# Not on the list. Perhaps subscribed as a Robogals member?
					if n.pk != 1:
						# Only do the user thing for The Amplifier (id = 1)
						return HttpResponse("B")  # Not subscribed
					try:
						for u in User.objects.filter(email=email):
							if u.email_newsletter_optin:
								u.email_newsletter_optin = False
								u.save()
								return HttpResponse("A")
						return HttpResponse("B")  # Not subscribed
					except User.DoesNotExist:
						return HttpResponse("B")  # Not subscribed
				ns.unsubscribed_date = datetime.now()
				ns.active = False
				ns.save()
				if n.pk == 1:
					for u in User.objects.filter(is_active=True, email=email, email_newsletter_optin=True):
						u.email_newsletter_optin = False
						u.save()
				return HttpResponse("A")
			else:
				return HttpResponse("-1")
		except KeyError:
			return HttpResponse("-1")
	else:
		return HttpResponse("-1")

def dlrapi(request):
	try:
		msg = SMSRecipient.objects.get(gateway_msg_id=request.GET['msgid'])
		dlr = request.GET['dlrstatus']
		if dlr == 'DELIVRD':
			msg.status = 12
		elif dlr == 'EXPIRED':
			msg.status = 14
		elif dlr == 'DELETED':
			msg.status = 15
		elif dlr == 'UNDELIV':
			msg.status = 13
		elif dlr == 'ACCEPTD':
			msg.status = 11
		elif dlr == 'REJECTD':
			msg.status = 16
		else:
			msg.status = 17
		msg.gateway_err = int(request.GET['dlr_err'])
		msg.save()
		return HttpResponse("OK\n")
	except Exception:
		return HttpResponse("-1\n")

class CSVUploadForm(forms.Form):
	csvfile = forms.FileField()

class WelcomeEmailForm(forms.Form):
	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		super(WelcomeEmailForm, self).__init__(*args, **kwargs)
		self.fields['from_address'].initial = user.email
		self.fields['reply_address'].initial = user.email
		self.fields['from_name'].initial = user.get_full_name()

	importaction = forms.ChoiceField(choices=((1,_('Add subscribers, and send welcome email')),(2,_('Add subscribers, with no further action')),(3,_('Add subscribers, and send welcome email if send_email = 1'))),initial=1)
	from_address = forms.CharField(max_length=256, required=True)
	reply_address = forms.CharField(max_length=256, required=True)
	from_name = forms.CharField(max_length=256, required=True)
	subject = forms.CharField(max_length=256, required=False)
	body = forms.CharField(widget=forms.Textarea, required=False)
	html = forms.BooleanField(required=False)

class DefaultsForm(forms.Form):
	type = forms.ModelChoiceField(queryset=SubscriberType.objects.all(), label=_('Subscriber type'), required=False)
	country = forms.ModelChoiceField(queryset=Country.objects.all(), label=_('Country'), required=False)
	details_verified = forms.BooleanField(label=_('Details verified'), required=False, initial=True)
	send_most_recent = forms.BooleanField(label=_('Send most recent newsletter upon subscribing'), required=False, initial=False)

@login_required
def importsubscribers(request, newsletter_id):
	newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
	if not (request.user.is_superuser or (request.user.is_staff and request.user.chapter.pk == 1)):
		raise Http404
	errmsg = None
	if request.method == 'POST':
		if request.POST['step'] == '1':
			form = CSVUploadForm(request.POST, request.FILES)
			welcomeform = WelcomeEmailForm(request.POST, user=request.user)
			defaultsform = DefaultsForm(request.POST)
			if form.is_valid() and welcomeform.is_valid() and defaultsform.is_valid():
				file = request.FILES['csvfile']
				tmppath = "/tmp/" + str(newsletter.pk) + request.user.username + str(time()) + ".csv"
				destination = open(tmppath, 'w')
				for chunk in file.chunks():
					destination.write(chunk)
				destination.close()
				fp = open(tmppath, 'rU')
				filerows = csv.reader(fp)
				defaults = defaultsform.cleaned_data
				welcomeemail = welcomeform.cleaned_data
				request.session['welcomeemail'] = welcomeemail
				request.session['defaults'] = defaults
				return render_to_response('import_subscribers_2.html', {'tmppath': tmppath, 'filerows': filerows, 'newsletter': newsletter}, context_instance=RequestContext(request))
		elif request.POST['step'] == '2':
			if 'tmppath' not in request.POST:
				return HttpResponseRedirect("/messages/newsletters/" + str(newsletter.pk) + "/import/")
			tmppath = request.POST['tmppath']
			fp = open(tmppath, 'rU')
			filerows = csv.reader(fp)
			welcomeemail = request.session['welcomeemail']
			defaults = request.session['defaults']
			try:
				users_imported = importcsv(filerows, welcomeemail, defaults, newsletter, request.user)
			except RgImportCsvException as e:
				errmsg = e.errmsg
				return render_to_response('import_subscribers_2.html', {'tmppath': tmppath, 'filerows': filerows, 'newsletter': newsletter, 'errmsg': errmsg}, context_instance=RequestContext(request))
			msg = _('%d subscribers imported!') % users_imported
			request.user.message_set.create(message=unicode(msg))
			del request.session['welcomeemail']
			del request.session['defaults']
			return HttpResponseRedirect("/messages/newsletters/" + str(newsletter.pk) + "/")
	else:
		form = CSVUploadForm()
		welcomeform = WelcomeEmailForm(None, user=request.user)
		defaultsform = DefaultsForm()
	return render_to_response('import_subscribers_1.html', {'newsletter': newsletter, 'form': form, 'welcomeform': welcomeform, 'defaultsform': defaultsform, 'errmsg': errmsg}, context_instance=RequestContext(request))

COMPULSORY_FIELDS = (
	('email', 'Email address'),
)

NAME_FIELDS = (
	('first_name', 'First name'),
	('last_name', 'Last name'),
	('company', 'Company name'),
)

ADVANCED_FIELDS = (
	('type', 'Type of subscriber'),
	('country', 'ISO two-letter country code'),
	('details_verified', 'Either \'True\' or \'False\', specifies whether this subscriber\'s details are known to be correct'),
)

ACTION_FIELDS = (
	('send_most_recent', 'Either \'True\' or \'False\', send the most recent newsletter to this user upon subscribing'),
	('send_email', 'Either \'True\' or \'False\', send the welcome email to this user upon subscribing'),
)

HELPINFO = (
	("Compulsory field", COMPULSORY_FIELDS),
	("Name fields", NAME_FIELDS),
	("Advanced fields", ADVANCED_FIELDS),
	("Action fields", ACTION_FIELDS)
)

@login_required
def importsubscribershelp(request, newsletter_id):
	newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
	if not (request.user.is_superuser or (request.user.is_staff and request.user.chapter.pk == 1)):
		raise Http404
	return render_to_response('import_users_help.html', {'HELPINFO': HELPINFO}, context_instance=RequestContext(request))

@login_required
def newslettercp(request, newsletter_id):
	newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
	getcontext().prec = 2
	subscribers = NewsletterSubscriber.objects.filter(newsletter=newsletter, active=True)
	total = len(subscribers)
	sub_totals = {}
	if newsletter.pk == 1:  # for The Amplifier only
		sub_totals["Robogals member"] = User.objects.filter(is_active=True, email_newsletter_optin=True).count()
		total += sub_totals["Robogals member"]
	for subscriber in subscribers:
		if subscriber.subscriber_type is None:
			if "<i>Unspecified</i>" in sub_totals:
				sub_totals['<i>Unspecified</i>'] += 1
			else:
				sub_totals['<i>Unspecified</i>'] = 1
		elif subscriber.subscriber_type.description in sub_totals:
			sub_totals[subscriber.subscriber_type.description] += 1
		else:
			sub_totals[subscriber.subscriber_type.description] = 1
	past_messages = EmailMessage.objects.filter(sender=newsletter.from_user).order_by('-date')
	history = []
	for message in past_messages:
		message_details = {}
		recipients = EmailRecipient.objects.filter(message=message)
		message_details['subject'] = message.subject
		message_details['total_sent'] = len(recipients)
		message_details['date'] = str(message.date.day) + "/" + str(message.date.month) + "/" + str(message.date.year)
		message_details['opened'] = len(EmailRecipient.objects.filter(message=message, status=7))
		message_details['percent'] = (Decimal((message_details['opened']))/(message_details['total_sent'])) * 100
		history.append(message_details)
	if not (request.user.is_superuser or (request.user.is_staff and request.user.chapter.pk == 1)):
		raise Http404
	return render_to_response('newsletter_cp.html', {'newsletter': newsletter, 'history': history, 'sub_totals': sorted(sub_totals.items(), key=itemgetter(1), reverse=True), 'total': total}, context_instance=RequestContext(request))
