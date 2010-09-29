from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from myrobogals.auth.models import Group
from myrobogals.auth.models import User
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient, Newsletter, NewsletterSubscriber
from myrobogals.rgprofile.models import UserList
from myrobogals.admin.widgets import FilteredSelectMultiple

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
			if int(data['from_type']) == 0:
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
					users = User.objects.filter(groups__in=data['chapters'], is_active=True, email_chapter_optin=True)
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

def writeamp(request):
	return HttpResponse("Write Amplifier")

def confirmamp(request):
	return HttpResponse("Confirm Amplifier")

def msghistory(request):
	return HttpResponse("Message History")
