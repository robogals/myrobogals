from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django import forms
from scichal.reg.models import JosDonations, JosDonate
from scichal.sc.models import Entrant
import re
import MySQLdb
from datetime import date

@login_required
def list(request):
	entrants = JosDonations.objects.all()
	return render_to_response('list.html', {'entrants': entrants}, context_instance=RequestContext(request))

class WriteEmailForm(forms.Form):
	to = forms.ChoiceField(choices=(
		(0,"OLD SYSTEM: Registered but not paid"),
		(1,"OLD SYSTEM: Registered and paid, but not submitted"),
		(2,"OLD SYSTEM: Registered, paid and submitted"),
		(3,"NEW SYSTEM: Registered but not submitted"),
		(4,"NEW SYSTEM: Registered and submitted"),
	), initial=3)
	from_name = forms.CharField(max_length=256)
	from_address = forms.CharField(max_length=256)
	reply_address = forms.CharField(max_length=256)
	subject = forms.CharField(max_length=256)
	body = forms.CharField(widget=forms.Textarea)
	html = forms.BooleanField(required=False)
	entry_year = forms.CharField(initial=str(date.today().year))

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
			action_id = int(data['to'])
			
			if action_id == 0:
				entrants = JosDonations.objects.filter(xaction_result = 'PENDING')
			elif action_id == 1 or action_id == 2:
				entrants = JosDonations.objects.filter(xaction_result = 'Completed ')
			elif action_id == 3 or action_id == 4:
				entrants = Entrant.objects.filter(entry_year=int(data['entry_year']))
			else:
				entrants = JosDonations.objects.none()
			
			if action_id == 2 or action_id == 4:
				submitted = 1    # Only take submitted
			elif action_id == 1 or action_id == 3:
				submitted = 0    # Only take non-submitted
			else:
				submitted = -1   # Don't care
	
			sentto = 0
			for e in entrants:
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
	return HttpResponseRedirect('/admin/sc/entrant/')

def home(request):
	return HttpResponseRedirect('/admin/sc/entrant/')
