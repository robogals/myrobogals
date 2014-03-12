from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template import Context, loader
from django.db import connection
connection.queries
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from myrobogals.rgteaching.models import School, DirectorySchool, StarSchoolDirectory, SchoolVisit, EventAttendee, Event, EventMessage, SchoolVisitStats, VISIT_TYPES_BASE, VISIT_TYPES_REPORT
from myrobogals.rgprofile.models import UserList
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient
#from myrobogals.auth.models import Group
import datetime
from myrobogals.rgmain.utils import SelectDateWidget, SelectTimeWidget
from myrobogals.auth.decorators import login_required
from myrobogals.auth.models import User, Group, MemberStatus
from myrobogals.admin.widgets import FilteredSelectMultiple
from tinymce.widgets import TinyMCE
from time import time, sleep
from pytz import utc
from myrobogals.rgmain.models import Country
from operator import itemgetter
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from myrobogals.rgmain.models import Subdivision
import json, urllib, urllib2, math

@login_required
def teachhome(request):
	return HttpResponseRedirect('/teaching/list/')
	#return render_to_response('teaching.html', {}, context_instance=RequestContext(request))

@login_required
def videotute(request):
	if not request.user.is_staff:
		raise Http404
	return render_to_response('video.html', {}, context_instance=RequestContext(request))

class SchoolVisitFormOne(forms.Form):
	ALLOW_RSVP_CHOICES = (
		(0, 'Allow anyone to RSVP'),
		(1, 'Only allow invitees to RSVP'),
		(2, 'Do not allow anyone to RSVP'),
	)

	school = forms.ModelChoiceField(queryset=School.objects.none(), help_text=_('If the school is not listed here, it first needs to be added in Workshops > Add School'))
	date = forms.DateField(label=_('School visit date'), widget=SelectDateWidget(years=range(2008,datetime.date.today().year + 3)), initial=datetime.date.today())
	start_time = forms.TimeField(label=_('Start time'), initial='10:00:00')
	end_time = forms.TimeField(label=_('End time'), initial='13:00:00')
	location = forms.CharField(label=_("Location"), help_text=_("Where the workshop is taking place, at the school or elsewhere (can differ from meeting location, see below)"))
	allow_rsvp = forms.ChoiceField(label=_("Allowed RSVPs"), choices=ALLOW_RSVP_CHOICES, initial=1)

	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(SchoolVisitFormOne, self).__init__(*args, **kwargs)
		if chapter == None:
			self.fields["school"].queryset = School.objects.all().order_by('name')
		else:
			self.fields["school"].queryset = School.objects.filter(chapter=chapter).order_by('name')

	def clean(self):
		cleaned_data = super(SchoolVisitFormOne, self).clean()
		start = cleaned_data.get("start_time")
		end = cleaned_data.get("end_time")
		if start and end and end <= start:
			msg = _("Start time must before End time.")
			self._errors["start_time"] = self.error_class([msg])
			self._errors["end_time"] = self.error_class([msg])
			del cleaned_data["start_time"]
			del cleaned_data["end_time"]
		return cleaned_data

class SchoolVisitFormTwo(forms.Form):
	meeting_location = forms.CharField(label=_("Meeting location"), help_text=_("Where people will meet at university to go as a group to the school, if applicable"), initial=_("N/A"), required=False)
	meeting_time = forms.TimeField(label=_("Meeting time"), help_text=_("What time people can meet to go to the school"), initial="09:30:00", required=False)
	contact = forms.CharField(label=_("Contact person"), max_length=128, required=False)
	contact_email = forms.CharField(label=_("Email"), max_length=128, required=False)
	contact_phone = forms.CharField(label=_("Phone"), max_length=32, required=False, help_text=_("Mobile number to call if people get lost"))

class SchoolVisitFormThree(forms.Form):
	numstudents = forms.CharField(label=_("Expected number of students"), required=False)
	yearlvl = forms.CharField(label=_("Year level"), required=False)
	numrobots = forms.CharField(label=_("Number of robots to bring"), required=False)
	lessonnum = forms.CharField(label=_("Lesson number"), required=False)
	toprint = forms.CharField(label=_("To print"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	tobring = forms.CharField(label=_("To bring"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	otherprep = forms.CharField(label=_("Other preparation"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	notes = forms.CharField(label=_("Other notes"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
		
@login_required
def editvisit(request, visit_id):
	chapter = request.user.chapter
	if request.user.is_staff:
		if visit_id == 0:
			v = SchoolVisit()
			v.chapter = chapter
			new = True
		else:
			v = get_object_or_404(SchoolVisit, pk=visit_id)
			new = False
		if (v.chapter != chapter) and not request.user.is_superuser:
			raise Http404
		if request.method == 'POST':
			if request.user.is_superuser:
				formpart1 = SchoolVisitFormOne(request.POST, chapter=None)
			else:
				formpart1 = SchoolVisitFormOne(request.POST, chapter=chapter)				
			formpart2 = SchoolVisitFormTwo(request.POST)
			formpart3 = SchoolVisitFormThree(request.POST)
			if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid():
				if visit_id == 0:
					v.chapter = chapter
					v.creator = request.user
				data = formpart1.cleaned_data
				v.school = data['school']
				v.visit_start = datetime.datetime.combine(data['date'], data['start_time'])
				v.visit_end = datetime.datetime.combine(data['date'], data['end_time'])
				v.location = data['location']
				v.allow_rsvp = data['allow_rsvp']
				date = data['date']
				data = formpart2.cleaned_data
				v.meeting_location = data['meeting_location']
				if data['meeting_time']:
					v.meeting_time = datetime.datetime.combine(date, data['meeting_time'])
				else:
					v.meeting_time = None
				v.contact = data['contact']
				v.contact_email = data['contact_email']
				v.contact_phone = data['contact_phone']
				data = formpart3.cleaned_data
				v.numstudents = data['numstudents']
				v.yearlvl = data['yearlvl']
				v.numrobots = data['numrobots']
				v.lessonnum = data['lessonnum']
				v.toprint = data['toprint']
				v.tobring = data['tobring']
				v.otherprep = data['otherprep']
				v.notes = data['notes']
				v.save()
				request.user.message_set.create(message=unicode(_("School visit info updated")))
				return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
		else:
			if request.user.is_superuser:
				formchapter = None
			else:
				formchapter = chapter
			if visit_id == 0:
				formpart1 = SchoolVisitFormOne(None, chapter=formchapter)
				formpart2 = SchoolVisitFormTwo()
				formpart3 = SchoolVisitFormThree()
			else:
				formpart1 = SchoolVisitFormOne({
					'school': v.school,
					'date': v.visit_start.date(),
					'start_time': v.visit_start.time(),
					'end_time': v.visit_end.time(),
					'location': v.location,
					'school': v.school_id,
					'allow_rsvp': v.allow_rsvp}, chapter=formchapter)
				formpart2 = SchoolVisitFormTwo({
					'meeting_location': v.meeting_location,
					'meeting_time': v.meeting_time,
					'contact': v.contact,
					'contact_email': v.contact_email,
					'contact_phone': v.contact_phone})
				formpart3 = SchoolVisitFormThree({
					'numstudents': v.numstudents,
					'yearlvl': v.yearlvl,
					'numrobots': v.numrobots,
					'lessonnum': v.lessonnum,
					'toprint': v.toprint,
					'tobring': v.tobring,
					'otherprep': v.otherprep,
					'notes': v.notes})

		return render_to_response('visit_edit.html', {'new': new, 'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3, 'chapter': chapter, 'visit_id': visit_id}, context_instance=RequestContext(request))
	else:
		raise Http404  # don't have permission to change

@login_required
def newvisit(request):
	return editvisit(request, 0)
	
@login_required
def newvisitwithschool(request, school_id):
	v = SchoolVisit()
	school = get_object_or_404(School, pk=school_id)
	v.chapter = request.user.chapter
	v.creator = request.user
	v.visit_start = datetime.datetime.now()
	v.visit_end = datetime.datetime.now()
	v.school = school
	v.location = "Enter location"
	v.save()
	return editvisit(request, v.id)

@login_required
def viewvisit(request, visit_id):
	chapter = request.user.chapter
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	if (v.chapter != chapter) and not request.user.is_superuser:
		raise Http404
	attended = EventAttendee.objects.filter(event=v, actual_status=1)
	attending = EventAttendee.objects.filter(event=v, rsvp_status=2)
	notattending = EventAttendee.objects.filter(event=v, rsvp_status=4)
	waitingreply = EventAttendee.objects.filter(event=v, rsvp_status=1)
	user_attended = False
	eventmessages = EventMessage.objects.filter(event=v)
	try:
		stats = SchoolVisitStats.objects.get(visit=v)
	except:
		stats = None
	try:
		ea = EventAttendee.objects.filter(event=visit_id, user=request.user)[0]
		user_rsvp_status = ea.rsvp_status
		user_attended = (ea.actual_status == 1)
	except IndexError:
		user_rsvp_status = 0
	return render_to_response('visit_view.html', {'chapter': chapter, 'v': v, 'stats': stats, 'attended': attended, 'attending': attending, 'notattending': notattending, 'waitingreply': waitingreply, 'user_rsvp_status': user_rsvp_status, 'user_attended': user_attended, 'eventmessages': eventmessages}, context_instance=RequestContext(request))

class ChapterSelector(forms.Form):
	chapter = forms.ModelChoiceField(queryset=Group.objects.filter(status__in=[0,2]), required=False)

@login_required
def listvisits(request):
	chapter = request.user.chapter
	if request.user.is_superuser:
		visits = SchoolVisit.objects.all()
		showall = True
		chapterform = ChapterSelector(request.GET)
		if chapterform.is_valid():
			chapter_filter = chapterform.cleaned_data['chapter']
			if chapter_filter:
				visits = visits.filter(chapter=chapter_filter)
	else:
		visits = SchoolVisit.objects.filter(chapter=chapter)
		showall = False
		chapterform = None
	return render_to_response('visit_list.html', {'chapterform': chapterform, 'showall': showall, 'chapter': chapter, 'visits': visits}, context_instance=RequestContext(request))

class VisitSelectorForm(forms.Form):
	start_date = forms.DateField(label='Visit start date', widget=SelectDateWidget(years=range(20011,datetime.date.today().year + 1)), initial=datetime.date.today())
	end_date = forms.DateField(label='Visit end date', widget=SelectDateWidget(years=range(2011,datetime.date.today().year + 1)), initial=datetime.date.today())

@login_required
def printlistvisits(request):
	if not request.user.is_staff:
		raise Http404
	if request.method == 'POST':
		theform = VisitSelectorForm(request.POST)
		if theform.is_valid():
			formdata = theform.cleaned_data
			chapter = request.user.chapter
			visits = SchoolVisit.objects.filter(visit_start__range=[formdata['start_date'],formdata['end_date']]).order_by('-visit_start')
			showall = True
			if not request.user.is_superuser:
				visits = visits.filter(chapter=chapter)
				showall = False
			return render_to_response('print_visit_list.html', {'showall': showall, 'chapter': chapter, 'visits': visits}, context_instance=RequestContext(request))
	theform = VisitSelectorForm()
	return render_to_response('print_visit_get_range.html', {'theform': theform}, context_instance=RequestContext(request))

class EmailModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.last_name + ", " + obj.first_name

class InviteForm(forms.Form):
	subject = forms.CharField(max_length=256, required=False)
	body = forms.CharField(widget=TinyMCE(attrs={'cols': 70}), required=False, initial=_("Hello,<br>\n<br>\nThere will be an upcoming Robogals school visit:<br>\nWhen: {visit.visit_start.year}-{visit.visit_start.month}-{visit.visit_start.day}, {visit.visit_start.hour}:{visit.visit_start.minute} to {visit.visit_end.hour}:{visit.visit_end.minute}<br>\nLocation: {visit.location}<br>\nSchool: {visit.school.name}<br>\n<br>\nTo accept or decline this invitation, please visit https://my.robogals.org/teaching/{visit.pk}/<br>\n<br>\nThanks,<br>\n<br>\n{user.chapter.name}"))
	memberselect = EmailModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple(_("Recipients"), False, attrs={'rows': 10}), required=False)
	list = forms.ModelChoiceField(queryset=UserList.objects.none(), required=False)
	action = forms.ChoiceField(choices=((1,_('Invite members')),(2,_('Add members as attending'))),initial=1)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		visit=kwargs['visit']
		del kwargs['visit']
		super(InviteForm, self).__init__(*args, **kwargs)
		self.fields['memberselect'].queryset = User.objects.filter(chapter=user.chapter, is_active=True, email_reminder_optin=True, pk__in=MemberStatus.objects.filter(statusType__pk=1, status_date_end__isnull=True).values_list('user_id', flat=True)).order_by('last_name')
		self.fields['list'].queryset = UserList.objects.filter(chapter=user.chapter)
		if visit.chapter.invite_email_subject:
			self.fields['subject'].initial = visit.chapter.invite_email_subject
		if visit.chapter.invite_email_msg:
			self.fields['body'].initial = visit.chapter.invite_email_msg

@login_required
def invitetovisit(request, visit_id):
	if not request.user.is_staff:
		raise Http404
	chapter = request.user.chapter
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	error = ''
	if (v.chapter != chapter) and not request.user.is_superuser:
		raise Http404
	if request.method == 'POST':
		inviteform = InviteForm(request.POST, user=request.user, visit=v)
		if inviteform.is_valid():
			data = inviteform.cleaned_data
			try:
				if data['action'] == '1':
					message = EmailMessage()
					message.subject = data['subject']
					try:
						message.body = data['body'].format(
							visit=v,
							user=request.user
						)
					except Exception:
						raise Exception(_('Email body contains invalid fields'))
					message.from_address = request.user.email
					message.reply_address = request.user.email
					message.sender = request.user
					#message.html = v.chapter.invite_email_html
					message.html = 1
					message.from_name = chapter.name
					
					# Don't send it yet until the recipient list is done
					message.status = -1
					# Save to database so we get a value for the primary key,
					# which we need for entering the recipient entries
					message.save()
	
				if request.POST['type'] == '1':
					users = User.objects.filter(chapter=chapter, is_active=True, email_reminder_optin=True)
				elif request.POST['type'] == '2':
					users = User.objects.filter(chapter=chapter, is_active=True, is_staff=True)
				elif request.POST['type'] == '4':
					users = User.objects.filter(chapter=chapter, is_active=True, email_reminder_optin=True, trained=True)
				elif request.POST['type'] == '5':
					ul = data['list']
					users = ul.users.all()
				else:
					users = data['memberselect']
	
				for one_user in users:
					if data['action'] == '1':
						recipient = EmailRecipient()
						recipient.message = message
						recipient.user = one_user
						recipient.to_name = one_user.get_full_name()
						recipient.to_address = one_user.email
						recipient.save()
					EventAttendee.objects.filter(user=one_user, event=v).delete()
					ea = EventAttendee()
					ea.event=v
					ea.user=one_user
					if data['action'] == '1':
						ea.rsvp_status=1
					if data['action'] == '2':
						ea.rsvp_status=2
					ea.actual_status=0
					ea.save()
				
				if data['action'] == '1':
					# Now mark it as OK to send. The email and all recipients are now in MySQL.
					# A background script on the server will process the queue.
					message.status = 0
					message.save()
				
				if data['action'] == '1':
					request.user.message_set.create(message=unicode(_("Invitations have been sent to the selected volunteers")))
				if data['action'] == '2':
					request.user.message_set.create(message=unicode(_("Selected volunteers have been added as attending")))
				return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
			except Exception as e:
				error = e.args[0]
	else:
		inviteform = InviteForm(None, user=request.user, visit=v)
	return render_to_response('visit_invite.html', {'inviteform': inviteform, 'visit_id': visit_id, 'error': error}, context_instance=RequestContext(request))
	
class EmailAttendeesForm(forms.Form):
	SCHEDULED_DATE_TYPES = (
		(1, 'My timezone'),
		(2, 'Recipients\' timezones'),
	)
	
	subject = forms.CharField(max_length=256, required=False)
	body = forms.CharField(widget=TinyMCE(attrs={'cols': 70}), required=False)
	memberselect = EmailModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple(_("Recipients"), False, attrs={'rows': 10}), required=False)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		visit=kwargs['visit']
		del kwargs['visit']
		super(EmailAttendeesForm, self).__init__(*args, **kwargs)
		id_list = EventAttendee.objects.filter(event=visit.id).values_list('user_id')
		self.fields['memberselect'].queryset = User.objects.filter(id__in = id_list, is_active=True, email_reminder_optin=True).order_by('last_name')
		
@login_required
def emailvisitattendees(request, visit_id):
	if not request.user.is_staff:
		raise Http404
	chapter = request.user.chapter
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	if (v.chapter != chapter) and not request.user.is_superuser:
		raise Http404
	if request.method == 'POST':
		emailform = EmailAttendeesForm(request.POST, user=request.user, visit=v)
		if emailform.is_valid():
			data = emailform.cleaned_data
			
			message = EmailMessage()
			message.subject = data['subject']
			message.body = data['body']
			message.from_address = request.user.email
			message.reply_address = request.user.email
			message.sender = request.user
			message.html = True
			message.from_name = chapter.name
			message.scheduled = False
				
			# Don't send it yet until the recipient list is done
			message.status = -1
			# Save to database so we get a value for the primary key,
			# which we need for entering the recipient entries
			message.save()
			
			
			# Start processing recipient list
			# Insert choices for attending, not attending etc here
			if request.POST['invitee_type'] == '1':
				id_list = EventAttendee.objects.filter(event=v.id).values_list('user_id')
				users = User.objects.filter(id__in = id_list, is_active=True, email_reminder_optin=True)
			elif request.POST['invitee_type'] == '2':
				id_list = EventAttendee.objects.filter(event=v.id, rsvp_status=2).values_list('user_id')
				users = User.objects.filter(id__in = id_list, is_active=True, email_reminder_optin=True)
			elif request.POST['invitee_type'] == '3':
				id_list = EventAttendee.objects.filter(event=v.id, rsvp_status=4).values_list('user_id')
				users = User.objects.filter(id__in = id_list, is_active=True, email_reminder_optin=True)
			elif request.POST['invitee_type'] == '4':
				id_list = EventAttendee.objects.filter(event=v.id, rsvp_status=1).values_list('user_id')
				users = User.objects.filter(id__in = id_list, is_active=True, email_reminder_optin=True)	
			elif request.POST['invitee_type'] == '5':
				users = data['memberselect']

			for one_user in users:
				recipient = EmailRecipient()
				recipient.message = message
				recipient.user = one_user
				recipient.to_name = one_user.get_full_name()
				recipient.to_address = one_user.email
				recipient.save()
				
			
			message.status = 0
			message.save()
			
			request.user.message_set.create(message=unicode(_("Email sent succesfully")))
			return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
	else:
		emailform = EmailAttendeesForm(None, user=request.user, visit=v)
	return render_to_response('visit_email.html', {'emailform': emailform, 'visit_id': visit_id}, context_instance=RequestContext(request))
	
class CancelForm(forms.Form):
	subject = forms.CharField(max_length=256, required=False,widget=forms.TextInput(attrs={'size':'40'}))
	body = forms.CharField(widget=TinyMCE(attrs={'cols': 70}), required=False)
	
	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		visit=kwargs['visit']
		del kwargs['visit']
		super(CancelForm, self).__init__(*args, **kwargs)
		self.fields['subject'].initial = "Visit to %s Cancelled" %visit.location
		self.fields['body'].initial = _("The workshop for %(school)s at %(starttime)s has been cancelled, sorry for any inconvenience." % {'school': visit.school, 'starttime': visit.visit_start})
		
@login_required
def cancelvisit(request, visit_id):
	if not request.user.is_staff:
		raise Http404
	chapter = request.user.chapter
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	if (v.chapter != chapter) and not request.user.is_superuser:
		raise Http404
	if request.method == 'POST':
		cancelform = CancelForm(request.POST, user=request.user, visit=v)
		if cancelform.is_valid():
			data = cancelform.cleaned_data
			message = EmailMessage()
			message.subject = data['subject']
			message.body = data['body']
			message.from_address = request.user.email
			message.reply_address = request.user.email
			message.sender = request.user
			message.html = True
			message.from_name = chapter.name
			message.scheduled = False
				
			# Don't send it yet until the recipient list is done
			message.status = -1
			# Save to database so we get a value for the primary key,
			# which we need for entering the recipient entries
			message.save()
			
			#Email everyone who has been invited.
			id_list = EventAttendee.objects.filter(event=v.id, rsvp_status=2).values_list('user_id')
			users = User.objects.filter(id__in = id_list, is_active=True, email_reminder_optin=True)

			for one_user in users:
				recipient = EmailRecipient()
				recipient.message = message
				recipient.user = one_user
				recipient.to_name = one_user.get_full_name()
				recipient.to_address = one_user.email
				recipient.save()

			message.status = 0
			message.save()
			Event.objects.filter(id = v.id).delete()
			request.user.message_set.create(message=unicode(_("Visit cancelled successfully")))
			return HttpResponseRedirect('/teaching/list/')
	else:
		cancelform = CancelForm(None, user=request.user, visit=v)
	return render_to_response('visit_cancel.html', {'cancelform': cancelform, 'visit_id': visit_id}, context_instance=RequestContext(request))

class DeleteForm(forms.Form):
	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		school=kwargs['school']
		del kwargs['school']
		super(DeleteForm, self).__init__(*args, **kwargs)
			
@login_required
def deleteschool(request, school_id):
	if not request.user.is_staff:
		raise Http404
	chapter = request.user.chapter
	s = get_object_or_404(School, pk=school_id)
	if (s.chapter != chapter):
		raise Http404
	if request.method == 'POST':
		deleteform = DeleteForm(request.POST, user=request.user, school=s)
		if SchoolVisit.objects.filter(school=s):
			request.user.message_set.create(message=unicode(_("You cannot delete this school as it has a visit in the database.")))
			return HttpResponseRedirect('/teaching/schools/')
		else:
			School.objects.filter(id = s.id).delete()
			request.user.message_set.create(message=unicode(_("School sucessfully deleted.")))
			return HttpResponseRedirect('/teaching/schools/')
	else:
		deleteform = DeleteForm(None, user=request.user, school=s)
	return render_to_response('school_delete.html', {'school': s}, context_instance=RequestContext(request))
	
@login_required
def listschools(request):
	if not request.user.is_staff:
		raise Http404
	chapter = request.user.chapter
	schools = School.objects.filter(chapter=chapter)
	return render_to_response('schools_list.html', {'chapter': chapter, 'schools': schools}, context_instance=RequestContext(request))

@login_required
def filllatlngschdir(request):
	if request.user.is_superuser:
		schools = DirectorySchool.objects.all()
		over_query_limit = False
		for school in schools:
			sleep(0.1)
			if (school.latitude == None) or (school.longitude == None):
				data = {}
				data['address'] = school.address_street
				data['components'] = '|locality:' + school.address_city + '|administrative_area:' + school.state_code() + '|country:' + school.address_country_id + '|postal_code:' + school.address_postcode
				data['sensor'] = 'false'
				url_values = urllib.urlencode(data)
				url = 'http://maps.googleapis.com/maps/api/geocode/json'
				full_url = url + '?' + url_values
				data = urllib2.urlopen(full_url, timeout=2)
				result = json.loads(data.read())
				if result['status'] == 'OK':
					school.latitude = result['results'][0]['geometry']['location']['lat']
					school.longitude = result['results'][0]['geometry']['location']['lng']
					school.save()
				elif result['status'] == 'ZERO_RESULTS':
					pass
				elif result['status'] == 'OVER_QUERY_LIMIT':
					msg = '- You have reached one day quota!'
					over_query_limit = True
					break
				elif result['status'] == 'REQUEST_DENIED':
					pass
				elif result['status'] == 'INVALID_REQUEST':
					pass
				else:
					pass
			else:
				pass
		if not over_query_limit:
			msg = 'Operation successful!'
	else:
		msg = '- You can not do this!'
	request.user.message_set.create(message=unicode(msg))
	return render_to_response('response.html', {}, context_instance=RequestContext(request))

@login_required
def schoolsdirectory(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
		raise Http404
	schools_list = DirectorySchool.objects.all()
	name = ''
	suburb = ''
	school_type = '-1'
	school_level = '-1'
	school_gender = '-1'
	starstatus = '-1'
	distance = ''
	origin = ''
	state = '1'
	if ('name' in request.GET) and (request.GET['name'] != ''):
		name = request.GET['name']
		schools_list = schools_list.filter(name__icontains=request.GET['name'])
	if ('suburb' in request.GET) and (request.GET['suburb'] != ''):
		suburb = request.GET['suburb']
		schools_list = schools_list.filter(address_city__icontains=request.GET['suburb'])
	if ('type' in request.GET) and (request.GET['type'] != '-1'):
		school_type = request.GET['type']
		schools_list = schools_list.filter(type=school_type)
	if ('level' in request.GET) and (request.GET['level'] != '-1'):
		school_level = request.GET['level']
		schools_list = schools_list.filter(level=school_level)
	if ('gender' in request.GET) and (request.GET['gender'] != '-1'):
		school_gender = request.GET['gender']
		schools_list = schools_list.filter(gender=school_gender)
	star_schools = StarSchoolDirectory.objects.filter(chapter=c).values_list('school_id', flat=True)
	if ('starstatus' in request.GET) and (request.GET['starstatus'] != '-1'):
		starstatus = request.GET['starstatus']
		if starstatus == '1':
			schools_list = schools_list.filter(id__in=star_schools)
		else:
			schools_list = schools_list.exclude(id__in=star_schools)
	sch_list = {}
	L1 = None
	G1 = None
	if ('distance' in request.GET) and (request.GET['distance'] != '') and ('origin' in request.GET) and (request.GET['origin'] != '') and ('state' in request.GET):
		distance = float(request.GET['distance'])
		origin = request.GET['origin']
		state = request.GET['state']
		subdiv = get_object_or_404(Subdivision, pk=state)
		try:
			data = {}
			data['components'] = 'locality:' + origin + '|administrative_area:' + subdiv.code + '|country:' + subdiv.country.pk
			data['sensor'] = 'false'
			url_values = urllib.urlencode(data)
			url = 'http://maps.googleapis.com/maps/api/geocode/json'
			full_url = url + '?' + url_values
			data = urllib2.urlopen(full_url, timeout=2)
			result = json.loads(data.read())
			if result['status'] == 'OK':
				L1 = float(result['results'][0]['geometry']['location']['lat'])
				G1 = float(result['results'][0]['geometry']['location']['lng'])
				for school in schools_list:
					if (school.latitude != None) and (school.longitude != None):
						L2 = school.latitude
						G2 = school.longitude
						DG = G2 - G1
						PI = 3.141592654
						# Great-circle distance
						D = 1.852 * 60.0 * (180.0 / PI) * math.acos(math.sin(math.radians(L1)) * math.sin(math.radians(L2)) + math.cos(math.radians(L1)) * math.cos(math.radians(L2)) * math.cos(math.radians(DG)))
						if D <= distance:
							sch_list[school.id] = D
				sch_list_sorted_keys = sorted(sch_list, key=sch_list.get)
				l = []
				for key in sch_list_sorted_keys:
					l.append(schools_list.get(pk=key))
				schools_list = l
			else:
				schools_list = schools_list.filter(address_state=subdiv, address_city__iexact=origin)
				request.user.message_set.create(message=unicode(_('- Sorry, suburb coordinate cannot be retrieved! Instead, schools within the same suburb are displayed.')))
		except:
			schools_list = schools_list.filter(address_state=subdiv, address_city__iexact=origin)
			request.user.message_set.create(message=unicode(_('- Sorry, suburb coordinate cannot be retrieved! Instead, schools within the same suburb are displayed')))

	paginator = Paginator(schools_list, 26)
	page = request.GET.get('page')
	try:
		schools = paginator.page(page)
	except EmptyPage:
		schools = paginator.page(paginator.num_pages)
	except:
		schools = paginator.page(1)
	copied_schools = School.objects.filter(chapter=c).values_list('name', flat=True)
	return render_to_response('schools_directory.html', {'schools': schools, 'subdivision': Subdivision.objects.all().order_by('id'), 'DirectorySchool': DirectorySchool, 'name': name, 'suburb': suburb, 'school_type': int(school_type), 'school_level': int(school_level), 'school_gender': int(school_gender), 'starstatus': int(starstatus), 'state': int(state), 'star_schools': star_schools, 'chapterurl': chapterurl, 'return': request.path + '?' + request.META['QUERY_STRING'], 'copied_schools': copied_schools, 'distance': distance, 'origin': origin, 'sch_list': sch_list, 'L1': L1, 'G1': G1}, context_instance=RequestContext(request))

@login_required
def starschool(request):
	if ('school_id' in request.GET) and ('chapterurl' in request.GET):
		s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
		c = get_object_or_404(Group, myrobogals_url__exact=request.GET['chapterurl'])
		if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
			raise Http404
		if StarSchoolDirectory.objects.filter(school=s, chapter=c):
			msg = '- The school "' + s.name + '" has been starred'
		else:
			starSchool = StarSchoolDirectory()
			starSchool.school = s
			starSchool.chapter = c
			starSchool.save()
			msg = 'The school "' + s.name + '" is starred'
		request.user.message_set.create(message=unicode(_(msg)))
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
	else:
		raise Http404

@login_required
def unstarschool(request):
	if ('school_id' in request.GET) and ('chapterurl' in request.GET):
		s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
		c = get_object_or_404(Group, myrobogals_url__exact=request.GET['chapterurl'])
		if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
			raise Http404
		starschools = StarSchoolDirectory.objects.filter(school=s, chapter=c)
		if starschools:
			for starschool in starschools:
				starschool.delete()
			msg = 'The school "' + s.name + '" is unstarred'
		else:
			msg = '- The school "' + s.name + '" is not starred'
		request.user.message_set.create(message=unicode(_(msg)))
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
	else:
		raise Http404

@login_required
def copyschool(request):
	if ('school_id' in request.GET) and ('chapterurl' in request.GET):
		s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
		c = get_object_or_404(Group, myrobogals_url__exact=request.GET['chapterurl'])
		if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
			raise Http404
		if School.objects.filter(chapter=c, name=s.name).count() > 0:
			msg = '- The school "' + s.name + '" is already already in your schools list'
		else:
			school = School()
			school.name = s.name
			school.chapter = c
			school.address_street = s.address_street
			school.address_city = s.address_city
			school.address_state = s.address_state.code
			school.address_postcode = s.address_postcode
			school.address_country = s.address_country
			school.contact_email = s.email
			school.contact_phone = s.phone
			school.save()
			msg = 'The school "' + s.name + '" has been added to your schools list. You can now create a workshop at this school.'
		request.user.message_set.create(message=unicode(_(msg)))
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
	else:
		raise Http404

# Custom field for school name
class SchoolNameField(forms.CharField):
	def __init__(self, *args, **kwargs):
		self.chapter=None
		self.school_id=None
		super(SchoolNameField, self).__init__(*args, **kwargs)

	# This function checks for the uniqueness of the school name within the chapter.
	# School names may not necessarily be unique globally across all chapters, thus
	# one cannot simply use the built-in Django functionality to specify this field
	# as a unique field.
	def clean(self, value):
		if value == '':
			if self.required:
				raise forms.ValidationError(_('This field is required.'))
			else:
				return ''
		if School.objects.filter(Q(chapter=self.chapter), ~Q(pk=self.school_id), Q(name=value)).count() > 0:
			raise forms.ValidationError(_('There is already a school with that name.'))
		else:
			return value

class SchoolFormPartOne(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		school_id=kwargs['school_id']
		del kwargs['school_id']
		super(SchoolFormPartOne, self).__init__(*args, **kwargs)
		self.fields['name'].chapter = chapter
		self.fields['name'].school_id = school_id
		self.fields['address_state'].initial = chapter.state
		if chapter.country:
			self.fields['address_country'].initial = chapter.country.pk
		else:
			self.fields['address_country'].initial = 'AU'

	name = SchoolNameField(max_length=128, label=_("Name"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	address_street = forms.CharField(label=_("Street"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	address_city = forms.CharField(label=_("City"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	address_state = forms.CharField(label=_("State"), required=True, widget=forms.TextInput(attrs={'size': '30'}),  help_text="Use the abbreviation, e.g. 'VIC' not 'Victoria'")
	address_postcode = forms.CharField(label=_("Postcode"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	address_country = forms.ModelChoiceField(label=_("Country"), queryset=Country.objects.all(), initial='AU')
	
class SchoolFormPartTwo(forms.Form):
	contact_person = forms.CharField(max_length=128, label=_("Name"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	contact_position = forms.CharField(max_length=128, label=_("Position"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	contact_email = forms.CharField(max_length=128, label=_("Email"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	contact_phone = forms.CharField(max_length=128, label=_("Phone"), required=False, widget=forms.TextInput(attrs={'size': '30'}))

class SchoolFormPartThree(forms.Form):
	notes = forms.CharField(label=_("Notes"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))

@login_required
def editschool(request, school_id):
	chapter = request.user.chapter
	if request.user.is_staff:
		if school_id == 0:
			s = School()
			s.chapter = chapter
			new = True
		else:
			s = get_object_or_404(School, pk=school_id)
			new = False
		if (s.chapter != chapter):
			raise Http404
		if request.method == 'POST':
			formpart1 = SchoolFormPartOne(request.POST, chapter=chapter, school_id=school_id)
			formpart2 = SchoolFormPartTwo(request.POST)
			formpart3 = SchoolFormPartThree(request.POST)
			if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid():
				if school_id == 0:
					s.chapter = chapter
					s.creator = request.user
				data = formpart1.cleaned_data
				s.name = data['name']
				s.address_street = data['address_street']
				s.address_city = data['address_city']
				s.address_state = data['address_state']
				s.address_postcode = data['address_postcode']
				s.address_country = data['address_country']
				data = formpart2.cleaned_data
				s.contact_person = data['contact_person']
				s.contact_position = data['contact_position']
				s.contact_email = data['contact_email']
				s.contact_phone = data['contact_phone']
				data = formpart3.cleaned_data
				s.notes = data['notes']
				s.save()
				request.user.message_set.create(message=unicode(_("School info updated")))
				return HttpResponseRedirect('/teaching/schools/')
		else:
			if school_id == 0:
				formpart1 = SchoolFormPartOne(None, chapter=chapter, school_id=school_id)
				formpart2 = SchoolFormPartTwo()
				formpart3 = SchoolFormPartThree()
			else:
				formpart1 = SchoolFormPartOne({
					'name': s.name,
					'address_street': s.address_street,
					'address_city': s.address_city,
					'address_state': s.address_state,
					'address_postcode': s.address_postcode,
					'address_country': s.address_country.pk}, chapter=chapter, school_id=school_id)
				formpart2 = SchoolFormPartTwo({
					'contact_person': s.contact_person,
					'contact_position': s.contact_position,
					'contact_email': s.contact_email,
					'contact_phone': s.contact_phone})
				formpart3 = SchoolFormPartThree({
					'notes': s.notes})

		return render_to_response('school_edit.html', {'new': new, 'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3, 'chapter': chapter, 'school_id': school_id}, context_instance=RequestContext(request))
	else:
		raise Http404  # don't have permission to change

@login_required
def newschool(request):
	return editschool(request, 0)

@login_required
def dorsvp(request, event_id, user_id, rsvp_status):
	event = get_object_or_404(Event, pk=event_id)
	user = get_object_or_404(User, pk=user_id)
	if event.status != 0:
		raise Http404
	if request.user.is_staff:
		EventAttendee.objects.filter(user=user, event=event).delete()
		ea = EventAttendee(user=user, event=event, rsvp_status=rsvp_status)
		ea.save()
	elif event.chapter == user.chapter and user == request.user:
		if event.allow_rsvp == 0:  # Allow anyone to RSVP
			EventAttendee.objects.filter(user=user, event=event).delete()
			ea = EventAttendee(user=user, event=event, rsvp_status=rsvp_status)
			ea.save()
		elif event.allow_rsvp == 1:  # Only allow invitees to RSVP
			if EventAttendee.objects.filter(user=user, event=event).count() > 0:
				EventAttendee.objects.filter(user=user, event=event).delete()
				ea = EventAttendee(user=user, event=event, rsvp_status=rsvp_status)
				ea.save()
	return HttpResponseRedirect('/teaching/' + str(event.pk) + '/')

class RSVPForm(forms.Form):
	leave_message = forms.BooleanField(required=False)
	message = forms.CharField(widget=TinyMCE(attrs={'cols': 60}), required=False)
	
	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		visit=kwargs['event']
		del kwargs['event']
		super(RSVPForm, self).__init__(*args, **kwargs)
		
def rsvp(request, event_id, user_id, rsvp_type):
	e = get_object_or_404(Event, pk=event_id)
	chapter = request.user.chapter
	if rsvp_type == 'yes':
		rsvp_id = 2
		rsvp_string = _("RSVP'd as attending")
		title_string = _("RSVP as attending")
	elif rsvp_type == 'no':
		rsvp_id = 4
		rsvp_string = _("RSVP'd as not attending")
		title_string = _("RSVP as not attending")
	elif rsvp_type == 'remove':
		title_string = _("Remove an invitee")
		rsvp_string = _("Removed from this event")
		rsvp_id = 0
	else:
		raise Http404
	if e.chapter != chapter and not request.user.is_superuser:
		raise Http404
	if request.method == 'POST':
		rsvpform = RSVPForm(request.POST, user=request.user, event=e)
		if rsvpform.is_valid():
			data = rsvpform.cleaned_data
			if data['leave_message'] == True:
				rsvpmessage = EventMessage()
				rsvpmessage.event = e
				rsvpmessage.user = request.user
				utc_dt = utc.localize(datetime.datetime.now())
				user_tz = request.user.tz_obj()
				user_dt = user_tz.normalize(utc_dt.astimezone(user_tz))
				rsvpmessage.date = user_dt.replace(tzinfo=None)
				rsvpmessage.message = data['message']
				rsvpmessage.save()
			request.user.message_set.create(message=unicode(rsvp_string))
			return dorsvp(request, event_id, user_id, rsvp_id)
	else:
		rsvpform = RSVPForm(None, user=request.user, event=e)
	return render_to_response('event_rsvp.html', {'rsvpform': rsvpform, 'title_string': title_string, 'event_id': event_id, 'user_id': user_id, 'rsvp_type': rsvp_type}, context_instance=RequestContext(request))

@login_required
def deletemessage(request, visit_id, message_id):
	if not request.user.is_staff:
		raise Http404
	chapter = request.user.chapter
	v = get_object_or_404(Event, pk=visit_id)
	m = get_object_or_404(EventMessage, pk=message_id)
	if (v.chapter != chapter) and not request.user.is_superuser:
		raise Http404
	if request.user.is_staff:	
		m.delete()
		request.user.message_set.create(message=unicode(_("Message deleted")))
	else:
		raise Http404
	return HttpResponseRedirect('/teaching/'+ str(v.pk) + '/')

class StatsModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.last_name + ", " + obj.first_name
	
class SchoolVisitStatsForm(forms.Form):
	visit_type = forms.ChoiceField(choices=VISIT_TYPES_BASE, required=False, help_text=_('For an explanation of each type please see <a href="%s" target="_blank">here</a> (opens in new window)') % '/teaching/statshelp/')
	primary_girls_first = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	primary_girls_repeat = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	primary_boys_first = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	primary_boys_repeat = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	high_girls_first = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	high_girls_repeat = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	high_boys_first = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	high_boys_repeat = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	other_girls_first = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	other_girls_repeat = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	other_boys_first = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	other_boys_repeat = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
	attended = StatsModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple(_("Invitees"), False, attrs={'rows': 8}), required=False)
	notes = forms.CharField(label=_("General notes"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	
	def clean(self):
		cleaned_data = self.cleaned_data
		return cleaned_data
	
	def __init__(self, *args, **kwargs):
		visit=kwargs['visit']
		del kwargs['visit']
		super(SchoolVisitStatsForm, self).__init__(*args, **kwargs)
		attending = EventAttendee.objects.filter(rsvp_status=2, event__id=visit.id).values_list('user_id')
		self.fields['attended'].queryset = User.objects.filter(is_active=True,chapter=visit.school.chapter).order_by('last_name')
		self.fields['attended'].initial = [u.pk for u in User.objects.filter(id__in = attending)]
		self.fields['visit_type'].initial = ''
		self.fields['primary_girls_first'].initial = visit.numstudents

@login_required
def stats(request, visit_id):
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	if v.school.chapter != request.user.chapter and not request.user.is_superuser:
		raise Http404
	if not request.user.is_staff:
		raise Http404
	if v.status != 0:
		request.user.message_set.create(message=unicode(_("- This workshop is already closed")))
		return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
	if not request.session.get('hoursPerPersonStage', False):
		request.session['hoursPerPersonStage'] = 1
		form = SchoolVisitStatsForm(None, visit = v)
		return render_to_response('visit_stats.html', {'form':form, 'visit_id':visit_id}, context_instance=RequestContext(request))
	if request.method == 'POST' and request.session['hoursPerPersonStage'] == 1:
		request.session['hoursPerPersonStage'] = 2
		form = SchoolVisitStatsForm(request.POST, visit = v)
		if form.is_valid():
			data = form.cleaned_data
			# Delete any existing stats that may exist for this visit.
			# This can happen if the user clicks back after entering stats
			# to change their stats
			v.schoolvisitstats_set.all().delete()
			# and add the new stats just entered
			stats = SchoolVisitStats()
			stats.visit = v
			stats.visit_type = data['visit_type']
			stats.primary_girls_first = data['primary_girls_first']
			stats.primary_girls_repeat = data['primary_girls_repeat']
			stats.primary_boys_first = data['primary_boys_first']
			stats.primary_boys_repeat = data['primary_boys_repeat']
			stats.high_girls_first = data['high_girls_first']
			stats.high_girls_repeat = data['high_girls_repeat']
			stats.high_boys_first = data['high_boys_first']
			stats.high_boys_repeat = data['high_boys_repeat']
			stats.other_girls_first = data['other_girls_first']
			stats.other_girls_repeat = data['other_girls_repeat']
			stats.other_boys_first = data['other_boys_first']
			stats.other_boys_repeat = data['other_boys_repeat']
			stats.notes = data['notes']
			stats.save()

			for attendee in data['attended']:
				list = EventAttendee.objects.filter(event__id=v.id).values_list('user_id', flat=True)
				if attendee.id not in list:
					newinvite = EventAttendee()
					newinvite.event = v
					newinvite.user = attendee
					newinvite.actual_status = 1
					newinvite.rsvp_status = 0
					newinvite.save()
			for person in EventAttendee.objects.filter(event__id=v.id):
				if person.user in data['attended']:
					person.actual_status = 1
					person.save()
				else:
					person.actual_status = 2
					person.save()
						
			defaultHours =  v.visit_end.hour - v.visit_start.hour
			if v.visit_end.minute > v.visit_start.minute:
				defaultHours += 1
			return render_to_response('visit_hoursPerPerson.html', {'attended': data['attended'], 'visit_id': visit_id, 'defaultHours': range(defaultHours)}, context_instance=RequestContext(request))
		else:
			request.session['hoursPerPersonStage'] = 1
			return render_to_response('visit_stats.html', {'form':form, 'visit_id':visit_id}, context_instance=RequestContext(request))
	elif request.method == 'POST' and request.session['hoursPerPersonStage'] == 2:
		raise Http404
	else:
		request.session['hoursPerPersonStage'] = 1
		form = SchoolVisitStatsForm(None, visit = v)
		return render_to_response('visit_stats.html', {'form':form, 'visit_id':visit_id}, context_instance=RequestContext(request))

@login_required
def reopenvisit(request, visit_id):
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	if v.school.chapter != request.user.chapter and not request.user.is_superuser:
		raise Http404
	if not request.user.is_staff:
		raise Http404
	if v.status != 1:
		request.user.message_set.create(message=unicode(_("- This workshop is already open!")))
		return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
	# Don't allow modifying of RRR stats - too many people have access
	if v.school.chapter.pk == 20 and not request.user.is_superuser:
		request.user.message_set.create(message=unicode(_("- To modify stats for Robogals Rural & Regional please contact support@robogals.org")))
		return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
	# Don't allow modifying of stats more than 6 months old - too risky
	if (datetime.datetime.now() - v.visit_start) > datetime.timedelta(days=180):
		request.user.message_set.create(message=unicode(_("- To protect against accidental deletion of old stats, workshops more than six months old cannot be re-opened. If you need to amend these stats please contact support@robogals.org")))
		return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
	if 'confirm' in request.GET:
		if request.GET['confirm'] == '1':
			v.schoolvisitstats_set.all().delete()
			v.status = 0
			v.save()
			request.user.message_set.create(message=unicode(_("Stats deleted and workshop re-opened.")))
			return HttpResponseRedirect('/teaching/' + str(visit_id) + '/')
		else:
			# Someone has set a random value for &confirm=
			raise Http404
	else:
		return render_to_response('visit_reopen.html', {'visit_id': visit_id}, context_instance=RequestContext(request))

@login_required
def statsHoursPerPerson(request, visit_id):
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	if v.school.chapter != request.user.chapter and not request.user.is_superuser:
		raise Http404
	if not request.user.is_staff:
		raise Http404
	if not request.session.get('hoursPerPersonStage', False):
		raise Http404
	if request.method == 'POST' and request.session['hoursPerPersonStage'] == 2:
		del request.session['hoursPerPersonStage']
		for person in EventAttendee.objects.filter(event__id=v.id):
			if str(person.user.pk) in request.POST.keys():
				person.hours = request.POST[str(person.user.pk)]
				person.actual_status = 1
				person.save()
			else:
				person.hours = 0
				person.actual_status = 2
				person.save()
		v.status = 1
		v.save()
		request.user.message_set.create(message=unicode(_("Stats saved successfully, visit closed.")))
		return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
	else:
		raise Http404

@login_required
def statshelp(request):
	if not request.user.is_staff:
		raise Http404
	return render_to_response('visit_stats_help.html', {}, context_instance=RequestContext(request))

class ReportSelectorForm(forms.Form):
	start_date = forms.DateField(label='Report start date', widget=SelectDateWidget(years=range(20011,datetime.date.today().year + 1)), initial=datetime.date.today())
	end_date = forms.DateField(label='Report end date', widget=SelectDateWidget(years=range(2011,datetime.date.today().year + 1)), initial=datetime.date.today())
	visit_type = forms.ChoiceField(choices=VISIT_TYPES_REPORT, required=True, help_text=_('For an explanation of each type please see <a href="%s" target="_blank">here</a> (opens in new window)') % '/teaching/statshelp/')
	printview = forms.BooleanField(label='Show printable version', required=False)
	
def xint(n):
	if n is None:
		return 0
	return int(n)

@login_required
def report_standard(request):
	# Redirect superusers to global reports
	if request.user.is_superuser:
		return HttpResponseRedirect('/globalreports/')
	else:
		# Redirect global and regional exec to global reports
		if not request.user.is_staff:
			raise Http404  # Don't allow ordinary users to see any reports
		else:
			if request.user.chapter.pk == 1:
				return HttpResponseRedirect('/globalreports/')
			elif request.user.chapter.parent:
				if request.user.chapter.parent.pk == 1:
					return HttpResponseRedirect('/globalreports/')
				else:
					pass
			else:
				pass

	# If we reached here, we must be a chapter exec
	if request.method == 'POST':
		theform = ReportSelectorForm(request.POST)
		if theform.is_valid():
			formdata = theform.cleaned_data
			event_id_list = Event.objects.filter(visit_start__range=[formdata['start_date'],formdata['end_date']], chapter=request.user.chapter, status=1).values_list('id',flat=True)
			stats_list = SchoolVisitStats.objects.filter(visit__id__in = event_id_list)
			event_list = SchoolVisit.objects.filter(event_ptr__in = event_id_list).values_list('school', flat=True)
			visit_ids = SchoolVisit.objects.filter(event_ptr__in = event_id_list).values_list('id')
			visited_schools = {}
			totals = {}
			attendance = {}
			attendance_filtered = {}
			volunteer_hours = 0
			totals['visits'] = 0
			totals['pgf'] = 0
			totals['pgr'] = 0
			totals['pbf'] = 0
			totals['pbr'] = 0
			totals['hgf'] = 0
			totals['hgr'] = 0
			totals['hbf'] = 0
			totals['hbr'] = 0
			totals['ogf'] = 0
			totals['ogr'] = 0
			totals['obf'] = 0
			totals['obr'] = 0
			event_list = set(event_list)
			for school_id in event_list:
				school = School.objects.get(id = school_id)
				visited_schools[school.name] = {}
				visited_schools[school.name]['name'] = school.name
				visited_schools[school.name]['visits'] = 0
				visited_schools[school.name]['pgf'] = 0
				visited_schools[school.name]['pgr'] = 0
				visited_schools[school.name]['pbf'] = 0
				visited_schools[school.name]['pbr'] = 0
				visited_schools[school.name]['hgf'] = 0
				visited_schools[school.name]['hgr'] = 0
				visited_schools[school.name]['hbf'] = 0
				visited_schools[school.name]['hbr'] = 0
				visited_schools[school.name]['ogf'] = 0
				visited_schools[school.name]['ogr'] = 0
				visited_schools[school.name]['obf'] = 0
				visited_schools[school.name]['obr'] = 0
				this_schools_visits = SchoolVisitStats.objects.filter(visit__school = school, visit__visit_start__range=[formdata['start_date'],formdata['end_date']], visit__status=1)
				if int(formdata['visit_type']) == -1:
					# include all stats categories
					pass
				elif int(formdata['visit_type']) == -2:
					# include both metro and regional robotics workshops
					this_schools_visits = this_schools_visits.filter(visit_type__in = [0,7])
				else:
					# only include specific stats category
					this_schools_visits = this_schools_visits.filter(visit_type = formdata['visit_type'])
				for each_visit in this_schools_visits:
					# totals for this school 
					visited_schools[school.name]['pgf'] += xint(each_visit.primary_girls_first)
					visited_schools[school.name]['pgr'] += xint(each_visit.primary_girls_repeat)
					visited_schools[school.name]['pbf'] += xint(each_visit.primary_boys_first)
					visited_schools[school.name]['pbr'] += xint(each_visit.primary_boys_repeat)
					visited_schools[school.name]['hgf'] += xint(each_visit.high_girls_first)
					visited_schools[school.name]['hgr'] += xint(each_visit.high_girls_repeat)
					visited_schools[school.name]['hbf'] += xint(each_visit.high_boys_first)
					visited_schools[school.name]['hbr'] += xint(each_visit.high_boys_repeat)
					visited_schools[school.name]['ogf'] += xint(each_visit.other_girls_first)
					visited_schools[school.name]['ogr'] += xint(each_visit.other_girls_repeat)
					visited_schools[school.name]['obf'] += xint(each_visit.other_boys_first)
					visited_schools[school.name]['obr'] += xint(each_visit.other_boys_repeat)
					visited_schools[school.name]['visits'] += 1					
					# overall totals
					totals['pgf'] += xint(each_visit.primary_girls_first)
					totals['pgr'] += xint(each_visit.primary_girls_repeat)
					totals['pbf'] += xint(each_visit.primary_boys_first)
					totals['pbr'] += xint(each_visit.primary_boys_repeat)
					totals['hgf'] += xint(each_visit.high_girls_first)
					totals['hgr'] += xint(each_visit.high_girls_repeat)
					totals['hbf'] += xint(each_visit.high_boys_first)
					totals['hbr'] += xint(each_visit.high_boys_repeat)
					totals['ogf'] += xint(each_visit.other_girls_first)
					totals['ogr'] += xint(each_visit.other_girls_repeat)
					totals['obf'] += xint(each_visit.other_boys_first)
					totals['obr'] += xint(each_visit.other_boys_repeat)	
					totals['visits'] += 1
				visited_schools[school.name]['gf'] = visited_schools[school.name]['pgf'] + visited_schools[school.name]['hgf'] + visited_schools[school.name]['ogf']
				visited_schools[school.name]['gr'] = visited_schools[school.name]['pgr'] + visited_schools[school.name]['hgr'] + visited_schools[school.name]['ogr']
				visited_schools[school.name]['bf'] = visited_schools[school.name]['pbf'] + visited_schools[school.name]['hbf'] + visited_schools[school.name]['obf']
				visited_schools[school.name]['br'] = visited_schools[school.name]['pbr'] + visited_schools[school.name]['hbr'] + visited_schools[school.name]['obr']
				if visited_schools[school.name]['visits'] == 0:
					del visited_schools[school.name]
				totals['gf'] = totals['pgf'] + totals['hgf'] + totals['ogf']
				totals['gr'] = totals['pgr'] + totals['hgr'] + totals['ogr']
				totals['bf'] = totals['pbf'] + totals['hbf'] + totals['obf']
				totals['br'] = totals['pbr'] + totals['hbr'] + totals['obr']
			# attendance reporting
			user_list = User.objects.filter(chapter=request.user.chapter)
						
			for volunteer in user_list:
				attendance[volunteer.get_full_name()] = [0,0]
				for attended in EventAttendee.objects.filter(actual_status = 1, event__id__in = visit_ids, user__id = volunteer.id):
					type_id = SchoolVisit.objects.get(pk=attended.event.pk).schoolvisitstats_set.all()[0].visit_type
					if int(formdata['visit_type']) == -1:
						# include all stats categories
						attendance[volunteer.get_full_name()][0] += 1
						volunteer_hours = attended.hours
						attendance[volunteer.get_full_name()][1] += int(volunteer_hours)
					elif int(formdata['visit_type']) == -2:
						# include both metro and regional robotics workshops
						if type_id == 0 or type_id == 7:
							attendance[volunteer.get_full_name()][0] += 1
							volunteer_hours = attended.hours
							attendance[volunteer.get_full_name()][1] += int(volunteer_hours)
					else:
						if type_id == int(formdata['visit_type']):
							attendance[volunteer.get_full_name()][0] += 1
							volunteer_hours = attended.hours
							attendance[volunteer.get_full_name()][1] += int(volunteer_hours)
								
			for name, num_visits in attendance.iteritems():
				if num_visits > 0:
					attendance_filtered[name] = num_visits
			attendance_sorted = sorted(attendance_filtered.iteritems(), key=itemgetter(1), reverse=True)
		else:
			totals = {}
			visited_schools = {}
			attendance_sorted = {}
	else:
		theform = ReportSelectorForm()
		totals = {}
		visited_schools = {}
		attendance_sorted = {}
	return render_to_response('stats_get_report.html',{'theform': theform, 'totals': totals, 'schools': sorted(visited_schools.iteritems()), 'attendance': attendance_sorted},context_instance=RequestContext(request))

@login_required
def report_global(request):
	# Allow superusers to see these reports
	if not request.user.is_superuser:
		# Allow global and regional exec to see these reports
		if not request.user.is_staff:
			raise Http404
		else:
			if request.user.chapter.pk == 1:
				pass
			elif request.user.chapter.parent:
				if request.user.chapter.parent.pk == 1:
					pass
				else:
					raise Http404
			else:
				raise Http404

	warning = ''
	printview = False
	if request.method == 'POST':
		theform = ReportSelectorForm(request.POST)
		if theform.is_valid():
			formdata = theform.cleaned_data
			printview = formdata['printview']
			chapter_totals = {}
			region_totals = {}
			global_totals = {}
			request.session['globalReportStartDate'] = formdata['start_date']
			request.session['globalReportEndDate'] = formdata['end_date']
			request.session['globalReportVisitType'] = formdata['visit_type']
			if formdata['start_date'] < datetime.date(2011, 2, 11):
				warning = 'Warning: Australian data prior to 10 September 2010 and UK data prior to 11 February 2011 may not be accurate'
			chapters = Group.objects.filter(exclude_in_reports=False)
			for chapter in chapters:
				chapter_totals[chapter.short_en] = {}
				chapter_totals[chapter.short_en]['workshops'] = 0
				chapter_totals[chapter.short_en]['schools'] = 0
				chapter_totals[chapter.short_en]['first'] = 0
				chapter_totals[chapter.short_en]['repeat'] = 0
				chapter_totals[chapter.short_en]['girl_workshops'] = 0
				chapter_totals[chapter.short_en]['weighted'] = 0
				event_id_list = Event.objects.filter(visit_start__range=[formdata['start_date'],formdata['end_date']], chapter=chapter, status=1).values_list('id',flat=True)
				event_list = SchoolVisit.objects.filter(event_ptr__in = event_id_list).values_list('school', flat=True)
				visit_ids = SchoolVisit.objects.filter(event_ptr__in = event_id_list).values_list('id')
				event_list = set(event_list)
				for school_id in event_list:
					this_schools_visits = SchoolVisitStats.objects.filter(visit__school__id = school_id, visit__visit_start__range=[formdata['start_date'],formdata['end_date']], visit__status=1)
					if int(formdata['visit_type']) == -1:
						# include all stats categories
						pass
					elif int(formdata['visit_type']) == -2:
						# include both metro and regional robotics workshops
						this_schools_visits = this_schools_visits.filter(visit_type__in = [0,7])
					else:
						# only include specific stats category
						this_schools_visits = this_schools_visits.filter(visit_type = formdata['visit_type'])
					if this_schools_visits:
						chapter_totals[chapter.short_en]['schools'] += 1
						for each_visit in this_schools_visits:
							chapter_totals[chapter.short_en]['first'] += xint(each_visit.primary_girls_first) + xint(each_visit.high_girls_first) + xint(each_visit.other_girls_first)
							chapter_totals[chapter.short_en]['repeat'] += xint(each_visit.primary_girls_repeat) + xint(each_visit.high_girls_repeat) + xint(each_visit.other_girls_repeat)
							chapter_totals[chapter.short_en]['workshops'] += 1	
				chapter_totals[chapter.short_en]['girl_workshops'] += chapter_totals[chapter.short_en]['first'] + chapter_totals[chapter.short_en]['repeat']
				chapter_totals[chapter.short_en]['weighted'] = chapter_totals[chapter.short_en]['first'] + (float(chapter_totals[chapter.short_en]['repeat'])/2)
				# Regional and Global Totals
				if chapter.parent:
					if chapter.parent.short_en not in region_totals:
						region_totals[chapter.parent.short_en] = {}
					for key, value in chapter_totals[chapter.short_en].iteritems():
						if key in region_totals[chapter.parent.short_en]:
							region_totals[chapter.parent.short_en][key] += value
						else:
							region_totals[chapter.parent.short_en][key] = value
						if key in global_totals:
							global_totals[key] += value
						else:
							global_totals[key] = value
					if chapter.parent.id == 1:
						del chapter_totals[chapter.short_en]
					elif chapter_totals[chapter.short_en]['workshops'] == 0:
						del chapter_totals[chapter.short_en]
				elif chapter.id == 1:
					del chapter_totals[chapter.short_en]
			del region_totals['Global']
		else:
			totals = {}
			chapter_totals = {}
			region_totals = {}
			global_totals = {}
	else:
		theform = ReportSelectorForm()
		chapter_totals = {}
		region_totals = {}
		global_totals = {}
	if request.user.is_superuser or request.user.chapter.id == 1:
		user_chapter_children = Group.objects.filter(exclude_in_reports=False).values_list('short_en', flat=True)
	else:
		user_chapter_children = Group.objects.filter(parent__pk=request.user.chapter.pk, exclude_in_reports=False).values_list('short_en', flat=True)
	if printview:
		return render_to_response('print_report.html',{'chapter_totals': sorted(chapter_totals.iteritems()),'region_totals': sorted(region_totals.iteritems()),'global': global_totals, 'warning': warning},context_instance=RequestContext(request))
	else:
		return render_to_response('stats_get_global_report.html',{'theform': theform, 'chapter_totals': sorted(chapter_totals.iteritems()),'region_totals': sorted(region_totals.iteritems()),'global': global_totals, 'warning': warning, 'user_chapter_children': set(user_chapter_children)},context_instance=RequestContext(request))

@login_required
def report_global_breakdown(request, chaptershorten):
	chapter = get_object_or_404(Group, short_en=chaptershorten)
	if (not request.user.is_staff) and (not request.user.is_superuser):
		raise Http404
	if (not chapter.parent) or (not chapter.parent.parent):
		raise Http404
	if (not request.user.is_superuser) and (request.user.chapter.pk != chapter.parent.pk) and (request.user.chapter.pk != chapter.parent.parent.pk):
		raise Http404
	if (not request.session.get('globalReportStartDate', False)) or (not request.session.get('globalReportEndDate', False)) or (not request.session.get('globalReportVisitType', False)):
		raise Http404
	start_date = request.session.get('globalReportStartDate', False)
	end_date = request.session.get('globalReportEndDate', False)
	visit_type = request.session.get('globalReportVisitType', False)
	chapter_totals = {}
	attendance = {}
	for u in User.objects.filter(chapter=chapter):
		attendance[u.get_full_name()]={}
		attendance[u.get_full_name()]['workshops'] = 0
		attendance[u.get_full_name()]['schools'] = 0
		attendance[u.get_full_name()]['first'] = 0
		attendance[u.get_full_name()]['repeat'] = 0
		attendance[u.get_full_name()]['girl_workshops'] = 0
		attendance[u.get_full_name()]['weighted'] = 0
	chapter_totals[chapter.short_en] = {}
	chapter_totals[chapter.short_en]['workshops'] = 0
	chapter_totals[chapter.short_en]['schools'] = 0
	chapter_totals[chapter.short_en]['first'] = 0
	chapter_totals[chapter.short_en]['repeat'] = 0
	chapter_totals[chapter.short_en]['girl_workshops'] = 0
	chapter_totals[chapter.short_en]['weighted'] = 0
	event_id_list = Event.objects.filter(visit_start__range=[start_date,end_date], chapter=chapter, status=1).values_list('id',flat=True)
	event_list = SchoolVisit.objects.filter(event_ptr__in = event_id_list).values_list('school', flat=True)
	visit_ids = SchoolVisit.objects.filter(event_ptr__in = event_id_list).values_list('id')
	event_list = set(event_list)
	for school_id in event_list:
		this_schools_visits = SchoolVisitStats.objects.filter(visit__school__id = school_id, visit__visit_start__range=[start_date,end_date], visit__status=1)
		if int(visit_type) == -1:
			# include all stats categories
			pass
		elif int(visit_type) == -2:
			# include both metro and regional robotics workshops
			this_schools_visits = this_schools_visits.filter(visit_type__in = [0,7])
		else:
			# only include specific stats category
			this_schools_visits = this_schools_visits.filter(visit_type = visit_type)
		if this_schools_visits:
			chapter_totals[chapter.short_en]['schools'] += 1
			for eventattendee in User.objects.filter(pk__in=EventAttendee.objects.filter(event__pk__in=this_schools_visits.values_list('visit__event_ptr_id', flat=True)).values_list('user_id', flat=True)):
				try:
					attendance[eventattendee.get_full_name()]['schools'] += 1
				except:
					pass
			for each_visit in this_schools_visits:
				first = xint(each_visit.primary_girls_first) + xint(each_visit.high_girls_first) + xint(each_visit.other_girls_first)
				chapter_totals[chapter.short_en]['first'] += first
				repeat = xint(each_visit.primary_girls_repeat) + xint(each_visit.high_girls_repeat) + xint(each_visit.other_girls_repeat)
				chapter_totals[chapter.short_en]['repeat'] += repeat
				chapter_totals[chapter.short_en]['workshops'] += 1	
				for eventattendee in EventAttendee.objects.filter(event__pk=each_visit.visit.event_ptr_id):
					try:
						attendance[eventattendee.user.get_full_name()]['first'] += first
						attendance[eventattendee.user.get_full_name()]['repeat'] += repeat
						attendance[eventattendee.user.get_full_name()]['workshops'] += 1
					except:
						pass
	chapter_totals[chapter.short_en]['girl_workshops'] += chapter_totals[chapter.short_en]['first'] + chapter_totals[chapter.short_en]['repeat']
	chapter_totals[chapter.short_en]['weighted'] = chapter_totals[chapter.short_en]['first'] + (float(chapter_totals[chapter.short_en]['repeat'])/2)
	for atten in attendance:
		attendance[atten]['girl_workshops'] += attendance[atten]['first'] + attendance[atten]['repeat']
		attendance[atten]['weighted'] = attendance[atten]['first'] + (float(attendance[atten]['repeat'])/2)
	return render_to_response('stats_global_report_breakdown.html',{'chapter_totals': sorted(chapter_totals.iteritems()), 'attendance': sorted(attendance.iteritems(), key=lambda item: item[1]['weighted'], reverse=True)},context_instance=RequestContext(request))
