# coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from myrobogals.auth.models import Group
from myrobogals.auth.models import User
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient, Newsletter, NewsletterSubscriber, PendingNewsletterSubscriber
from myrobogals.rgprofile.models import UserList
from myrobogals.admin.widgets import FilteredSelectMultiple
from myrobogals.settings import API_SECRET, SECRET_KEY
from django.forms.fields import email_re
from hashlib import md5
from urllib import unquote_plus
from datetime import datetime

def validate_sms_chars(text):
	matches = re.compile(u'^[a-z|A-Z|0-9|\\n|\\r|@|£|\$|¥|è|é|ù|ì|ò|Ç|Ø|ø|Å|å|Δ|Φ|Γ|Λ|Ω|Π|Ψ|Σ|Θ|Ξ|_|\^|{|}|\\\\|\[|~|\]|\||€|Æ|æ|ß|É| |!|"|#|¤|\%|&|\'|(|)|\*|\+|\,|\-|\.|\/|:|;|<|=|>|\?|¡|Ä|Ö|Ñ|Ü|§|¿|ä|ö|ñ|ü|à]+$').findall(text)
	if matches == []:
		return False
	else:
		return True

def list(request):
	return HttpResponse("List Messages")

def view(request, msgid):
	return HttpResponse("View Message %s" % msgid)

def createnew(request):
	return HttpResponse("Create New Message")

def writesms(request):
	return HttpResponse("Write SMS")

def confirmsms(request):
	return HttpResponse("Confirm SMS")

class EmailModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.last_name + ", " + obj.first_name
        #return obj.last_name + ", " + obj.first_name + " (" + obj.email + ")"

class WriteEmailForm(forms.Form):
	subject = forms.CharField(max_length=256)
	body = forms.CharField(widget=forms.Textarea)
	from_type = forms.ChoiceField(choices=((0,"Robogals"),(1,"Chapter name"),(2,"Your name")), initial=1)
	recipients = EmailModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple("Recipients", False, attrs={'rows': 10}), required=False)
	chapters = forms.ModelMultipleChoiceField(queryset=Group.objects.all().order_by('name'), widget=FilteredSelectMultiple("Chapters", False, attrs={'rows': 10}), required=False)
	chapters_exec = forms.ModelMultipleChoiceField(queryset=Group.objects.all().order_by('name'), widget=FilteredSelectMultiple("Chapters", False, attrs={'rows': 10}), required=False)
	list = forms.ModelChoiceField(queryset=UserList.objects.none(), required=False)
	newsletters = forms.ModelChoiceField(queryset=Newsletter.objects.all(), required=False)
	html = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		super(WriteEmailForm, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['recipients'].queryset = User.objects.filter(is_active=True, email_chapter_optin=True).order_by('last_name')
		else:
			self.fields['recipients'].queryset = User.objects.filter(groups=user.chapter(), is_active=True, email_chapter_optin=True).order_by('last_name')
		self.fields['list'].queryset = UserList.objects.filter(chapter=user.chapter())
		self.fields['from_type'].choices = (
			(0, "Robogals <" + user.email + ">"),
			(1, user.chapter().name + " <" + user.email + ">"),
			(2, user.get_full_name() + " <" + user.email + ">")
		)

def writeemail(request):
	if request.method == 'POST':
		emailform = WriteEmailForm(request.POST, user=request.user)
		if emailform.is_valid():
			data = emailform.cleaned_data
			message = EmailMessage()
			message.subject = data['subject']
			message.body = data['body']
			message.from_address = request.user.email
			message.reply_address = request.user.email
			message.sender = request.user
			message.html = data['html']
			if request.POST['type'] == '4':
				n = data['newsletters']
				message.from_name = n.from_name
				message.from_address = n.from_email
				message.reply_address = n.from_email
				message.sender = n.from_user
				message.html = True
			elif int(data['from_type']) == 0:
				message.from_name = "Robogals"
			elif int(data['from_type']) == 1:
				message.from_name = request.user.chapter().name
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
					#users = User.objects.filter(groups__in=data['chapters'], is_active=True, email_chapter_optin=True)
					raise Exception
				else:
					users = User.objects.filter(groups=request.user.chapter(), is_active=True, email_chapter_optin=True)
			elif request.POST['type'] == '2':
				if request.user.is_superuser:
					users = User.objects.filter(groups__in=data['chapters_exec'], is_active=True, is_staff=True)
				else:
					users = User.objects.filter(groups=request.user.chapter(), is_active=True, is_staff=True)
			elif request.POST['type'] == '5':
				ul = data['list']
				users = ul.users.all()
			elif request.POST['type'] == '4':
				if request.user.is_superuser:
					# Special rule for The Amplifier
					if data['newsletters'].pk == 1:
						users = User.objects.filter(is_active=True, email_newsletter_optin=True)
					else:
						users = User.objects.none()
			else:
				users = data['recipients']

			for one_user in users:
				recipient = EmailRecipient()
				recipient.message = message
				recipient.user = one_user
				recipient.to_name = one_user.get_full_name()
				recipient.to_address = one_user.email
				recipient.save()
			
			if request.POST['type'] == '4' and request.user.is_superuser:
				for one_subscriber in NewsletterSubscriber.objects.filter(newsletter=data['newsletters'], active=True):
					recipient = EmailRecipient()
					recipient.message = message
					recipient.user = None
					recipient.to_name = one_subscriber.first_name + " " + one_subscriber.last_name
					recipient.to_address = one_subscriber.email
					recipient.save()
			
			# Now mark it as OK to send. The email and all recipients are now in MySQL.
			# A background script on the server will process the queue.
			message.status = 0
			message.save()
			
			return HttpResponseRedirect('/messages/email/done/')
	else:
		emailform = WriteEmailForm(None, user=request.user)
	return render_to_response('email_write.html', {'emailform': emailform,}, context_instance=RequestContext(request))

def emaildone(request):
	return render_to_response('email_done.html', None, context_instance=RequestContext(request))

def msghistory(request):
	return HttpResponse("Message History")

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
					return HttpResponse("B")  # Not subscribed
				ns.unsubscribed_date = datetime.now()
				ns.active = False
				ns.save()
				return HttpResponse("A")				
			else:
				return HttpResponse("-1")
		except KeyError:
			return HttpResponse("-1")
	else:
		return HttpResponse("-1")
