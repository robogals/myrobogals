from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from reg.models import JosDonations, JosDonate
import re
import MySQLdb

def list(request):
	entrants = JosDonations.objects.all()
	return render_to_response('list.html', {'entrants': entrants}, context_instance=RequestContext(request))

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
	0,
	NOW(),
	1,
	0)
	""" % (thank_you_subject, re.escape(thank_you_body.replace("\\,", ",")), admin_email, admin_email))
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
	NULL)""" % (c.lastrowid, e.mentor(), e.email))
	e.xaction_result = 'Completed '
	e.save()
	return HttpResponseRedirect('/admin/reg/josdonations/')

def home(request):
	return HttpResponseRedirect('/admin/reg/josdonations/')
