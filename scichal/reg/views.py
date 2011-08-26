from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django import forms
from reg.models import JosDonations, JosDonate
import re
import MySQLdb

@login_required
def list(request):
	entrants = JosDonations.objects.all()
	return render_to_response('list.html', {'entrants': entrants}, context_instance=RequestContext(request))

class WriteEmailForm(forms.Form):
	to = forms.ChoiceField(choices=((0,"Registered but not paid"),(1,"Registered and paid, but not submitted"),(2,"Registered, paid and submitted")))
	from_name = forms.CharField(max_length=256)
	from_address = forms.CharField(max_length=256)
	reply_address = forms.CharField(max_length=256)
	subject = forms.CharField(max_length=256)
	body = forms.CharField(widget=forms.Textarea)
	html = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		super(WriteEmailForm, self).__init__(*args, **kwargs)
		self.fields['from_name'].initial = user.get_full_name()
		self.fields['from_address'].initial = user.email
		self.fields['reply_address'].initial = user.email

@login_required
def send_email(request):
	if request.method == 'POST':
		emailform = WriteEmailForm(request.POST, user=request.user)
		if emailform.is_valid():
			data = emailform.cleaned_data
		
			db=MySQLdb.connect(user="myrobogals",passwd="myrobogals", db="myrobogals")
			c=db.cursor()
			if data['html']:
				html = 1
			else:
				html = 0
			
			# Create message
			c.execute("""INSERT INTO rgmessages_emailmessage
			(`subject`,
			`body`,
			`from_name`,
			`from_address`,
			`reply_address`,
			`sender_id`,
			`status`,
			`date`,
			`html`,
			`scheduled`)
			VALUES
			("%s",
			"%s",
			"%s",
			"%s",
			"%s",
			694,
			-1,
			NOW(),
			%d,
			0)
			""" % (re.escape(data['subject']),
				re.escape(data['body']),
				re.escape(data['from_name']),
				re.escape(data['from_address']),
				re.escape(data['reply_address']),
				html))
			email_id = c.lastrowid
			
			# Add recipients
			if int(data['to']) == 0:
				entrants = JosDonations.objects.filter(xaction_result = 'PENDING')
			elif (int(data['to']) == 1 or int(data['to']) == 2):
				entrants = JosDonations.objects.filter(xaction_result = 'Completed ')
			else:
				entrants = JosDonations.objects.none()
			
			if int(data['to']) == 2:
				submitted = 1    # Only take submitted
			elif int(data['to']) == 1:
				submitted = 0    # Only take non-submitted
			else:
				submitted = -1   # Don't care
	
			sentto = 0
			for e in entrants:
				print str(e)
				if submitted == 1:
					if not e.has_submitted():
						continue
				elif submitted == 0:
					if e.has_submitted():
						continue
				c.execute("""INSERT INTO rgmessages_emailrecipient
				(`message_id`,
				`user_id`,
				`to_name`,
				`to_address`,
				`status`,
				`scheduled_date`)
				VALUES
				(%d,
				NULL,
				"%s",
				"%s",
				0,
				NOW())""" % (email_id, e.mentor(), e.email))
				sentto += 1

			# All recipients added, ready to send!
			c.execute("UPDATE rgmessages_emailmessage SET `status` = 0 WHERE `id` = " + str(email_id))
			return render_to_response('email_done.html', {'sentto': sentto}, context_instance=RequestContext(request))
		else:
			return render_to_response('email_form.html', {'emailform': emailform}, context_instance=RequestContext(request))
	else:
		emailform = WriteEmailForm(None, user=request.user)
		return render_to_response('email_form.html', {'emailform': emailform}, context_instance=RequestContext(request))

@login_required
def mark_paid(request, entrant_id):
	e = get_object_or_404(JosDonations, pk=entrant_id)
	o = JosDonate.objects.get(id=1)
	optionstring = o.options
	done = 0
	while 1:
		result = re.match("([^,\\\\]|\\\\.)+", optionstring)
		if result == None:
			break
		results = result.group(0).split('=', 1)
		#print results[0]
		if results[0] == "admin_email":
			admin_email = results[1]
			done += 1
		elif results[0] == "thank_you_subject":
			thank_you_subject = results[1]
			done += 1
		elif results[0] == "thank_you_body":
			thank_you_body = results[1]
			done += 1
		if done == 3:
			break
		optionstring = optionstring[len(result.group(0))+1:]
		#print optionstring
		if len(optionstring) == 0:
			break
	db=MySQLdb.connect(user="myrobogals",passwd="myrobogals", db="myrobogals")
	c=db.cursor()
	c.execute("""INSERT INTO rgmessages_emailmessage
	(`subject`,
	`body`,
	`from_name`,
	`from_address`,
	`reply_address`,
	`sender_id`,
	`status`,
	`date`,
	`html`,
	`scheduled`)
	VALUES
	("%s",
	"%s",
	"Robogals Science Challenge",
	"%s",
	"%s",
	694,
	-1,
	NOW(),
	1,
	0)
	""" % (thank_you_subject, re.escape(thank_you_body.replace("\\,", ",")), admin_email, admin_email))
	email_id = c.lastrowid
	c.execute("""INSERT INTO rgmessages_emailrecipient
	(`message_id`,
	`user_id`,
	`to_name`,
	`to_address`,
	`status`,
	`scheduled_date`)
	VALUES
	(%d,
	NULL,
	"%s",
	"%s",
	0,
	NOW())""" % (email_id, e.mentor(), e.email))
	c.execute("UPDATE rgmessages_emailmessage SET `status` = 0 WHERE `id` = " + str(email_id))
	e.xaction_result = 'Completed '
	e.save()
	return HttpResponseRedirect('/admin/reg/josdonations/')

def home(request):
	return HttpResponseRedirect('/admin/reg/josdonations/')
