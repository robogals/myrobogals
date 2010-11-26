from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from myrobogals.rgteaching.models import School, SchoolVisit, EventAttendee, Event
from myrobogals.rgprofile.models import UserList
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient
#from myrobogals.auth.models import Group
import datetime
from myrobogals.rgmain.utils import SelectDateWidget
from myrobogals.auth.decorators import login_required
from myrobogals.auth.models import User
from myrobogals.admin.widgets import FilteredSelectMultiple

@login_required
def teachhome(request):
	return render_to_response('teaching.html', {}, context_instance=RequestContext(request))

class SchoolVisitFormOne(forms.Form):
	ALLOW_RSVP_CHOICES = (
		(0, 'Allow anyone to RSVP'),
		(1, 'Only allow invitees to RSVP'),
		(2, 'Do not allow anyone to RSVP'),
	)

	school = forms.ModelChoiceField(queryset=School.objects.none(), help_text=_('If the school is not listed here, it first needs to be added in Teaching > Add School'))
	date = forms.DateField(label=_('School visit date'), widget=SelectDateWidget(years=range(2008,datetime.date.today().year + 3)), initial=datetime.date.today())
	start_time = forms.TimeField(label=_('Start time'), initial='10:00:00')
	end_time = forms.TimeField(label=_('End time'), initial='13:00:00')
	location = forms.CharField(label=_("Location"), help_text=_("Where the teaching is taking place, at the school or elsewhere (can differ from meeting location, see below)"))
	allow_rsvp = forms.ChoiceField(label=_("Allowed RSVPs"), choices=ALLOW_RSVP_CHOICES, initial=1)

	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(SchoolVisitFormOne, self).__init__(*args, **kwargs)
		self.fields["school"].queryset = School.objects.filter(chapter=chapter)

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
	chapter = request.user.chapter()
	if request.user.is_staff:
		if visit_id == 0:
			v = SchoolVisit()
			v.chapter = chapter
			new = True
		else:
			v = get_object_or_404(SchoolVisit, pk=visit_id)
			new = False
		if (v.chapter != chapter):
			raise Http404
		if request.method == 'POST':
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
				request.user.message_set.create(message="School visit info updated")
				return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
		else:
			if visit_id == 0:
				formpart1 = SchoolVisitFormOne(None, chapter=chapter)
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
					'allow_rsvp': v.allow_rsvp}, chapter=chapter)
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
def viewvisit(request, visit_id):
	chapter = request.user.chapter()
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	if (v.chapter != chapter):
		raise Http404
	attended = EventAttendee.objects.filter(event=v, actual_status=1)
	attending = EventAttendee.objects.filter(event=v, rsvp_status=2)
	notattending = EventAttendee.objects.filter(event=v, rsvp_status=4)
	waitingreply = EventAttendee.objects.filter(event=v, rsvp_status=1)
	user_attended = False
	try:
		ea = EventAttendee.objects.filter(event=visit_id, user=request.user)[0]
		user_rsvp_status = ea.rsvp_status
		user_attended = (ea.actual_status == 1)
	except IndexError:
		user_rsvp_status = 0
	return render_to_response('visit_view.html', {'chapter': chapter, 'v': v, 'attended': attended, 'attending': attending, 'notattending': notattending, 'waitingreply': waitingreply, 'user_rsvp_status': user_rsvp_status, 'user_attended': user_attended}, context_instance=RequestContext(request))

@login_required
def listvisits(request):
	chapter = request.user.chapter()
	visits = SchoolVisit.objects.filter(chapter=chapter)
	return render_to_response('visit_list.html', {'chapter': chapter, 'visits': visits}, context_instance=RequestContext(request))

class EmailModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.last_name + ", " + obj.first_name

class InviteForm(forms.Form):
	subject = forms.CharField(max_length=256, required=False)
	body = forms.CharField(widget=forms.Textarea, required=False)
	memberselect = EmailModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple("Recipients", False, attrs={'rows': 10}), required=False)
	list = forms.ModelChoiceField(queryset=UserList.objects.none(), required=False)
	html = forms.BooleanField(required=False)
	action = forms.ChoiceField(choices=((1,'Invite members'),(2,'Add members as attending')),initial=1)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		visit=kwargs['visit']
		del kwargs['visit']
		super(InviteForm, self).__init__(*args, **kwargs)
		self.fields['memberselect'].queryset = User.objects.filter(groups=user.chapter(), is_active=True, email_reminder_optin=True).order_by('last_name')
		self.fields['list'].queryset = UserList.objects.filter(chapter=user.chapter())
		self.fields['body'].initial = "Hello,\n\nThere will be an upcoming Robogals school visit:\n"
		self.fields['body'].initial += "Date: " + visit.start_date_formatted() + ", " + str(visit.visit_start.time()) + " to " + str(visit.visit_end.time())
		self.fields['body'].initial += "\nLocation: " + visit.location + "\nSchool: " + visit.school.name
		self.fields['body'].initial += "\n\nTo accept or decline this invitation, please visit https://my.robogals.org/teaching/" + str(visit.pk) + "/\n\nThanks,\n\n" + user.chapter().name + "\n"

@login_required
def invitetovisit(request, visit_id):
	chapter = request.user.chapter()
	v = get_object_or_404(SchoolVisit, pk=visit_id)
	if (v.chapter != chapter):
		raise Http404
	if request.method == 'POST':
		inviteform = InviteForm(request.POST, user=request.user, visit=v)
		if inviteform.is_valid():
			data = inviteform.cleaned_data
			if data['action'] == '1':
				message = EmailMessage()
				message.subject = data['subject']
				message.body = data['body']
				message.from_address = request.user.email
				message.reply_address = request.user.email
				message.sender = request.user
				message.html = data['html']
				message.from_name = chapter.name
				
				# Don't send it yet until the recipient list is done
				message.status = -1
				# Save to database so we get a value for the primary key,
				# which we need for entering the recipient entries
				message.save()

			if request.POST['type'] == '1':
				users = User.objects.filter(groups=chapter, is_active=True, email_reminder_optin=True)
			elif request.POST['type'] == '2':
				users = User.objects.filter(groups=chapter, is_active=True, is_staff=True)
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
				request.user.message_set.create(message="Invitations have been sent to the selected volunteers")
			if data['action'] == '2':
				request.user.message_set.create(message="Selected volunteers have been added as attending")
			return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
	else:
		inviteform = InviteForm(None, user=request.user, visit=v)
	return render_to_response('visit_invite.html', {'inviteform': inviteform, 'visit_id': visit_id}, context_instance=RequestContext(request))

@login_required
def listschools(request):
	chapter = request.user.chapter()
	schools = School.objects.filter(chapter=chapter)
	return render_to_response('schools_list.html', {'chapter': chapter, 'schools': schools}, context_instance=RequestContext(request))

class SchoolFormPartOne(forms.Form):
	name = forms.CharField(max_length=128, label=_("Name"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	address = forms.CharField(label=_("Address"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))

class SchoolFormPartTwo(forms.Form):
	contact_person = forms.CharField(max_length=128, label=_("Name"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	contact_position = forms.CharField(max_length=128, label=_("Position"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	contact_email = forms.CharField(max_length=128, label=_("Email"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	contact_phone = forms.CharField(max_length=128, label=_("Phone"), required=False, widget=forms.TextInput(attrs={'size': '30'}))

class SchoolFormPartThree(forms.Form):
	notes = forms.CharField(label=_("Notes"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))

@login_required
def editschool(request, school_id):
	chapter = request.user.chapter()
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
			formpart1 = SchoolFormPartOne(request.POST)
			formpart2 = SchoolFormPartTwo(request.POST)
			formpart3 = SchoolFormPartThree(request.POST)
			if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid():
				if school_id == 0:
					s.chapter = chapter
					s.creator = request.user
				data = formpart1.cleaned_data
				s.name = data['name']
				s.address = data['address']
				data = formpart2.cleaned_data
				s.contact_person = data['contact_person']
				s.contact_position = data['contact_position']
				s.contact_email = data['contact_email']
				s.contact_phone = data['contact_phone']
				data = formpart3.cleaned_data
				s.notes = data['notes']
				s.save()
				return HttpResponseRedirect('/teaching/schools/')
		else:
			if school_id == 0:
				formpart1 = SchoolFormPartOne()
				formpart2 = SchoolFormPartTwo()
				formpart3 = SchoolFormPartThree()
			else:
				formpart1 = SchoolFormPartOne({
					'name': s.name,
					'address': s.address})
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
	elif event.chapter == user.chapter() and user == request.user:
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

def rsvpyes(request, event_id, user_id):
	return dorsvp(request, event_id, user_id, 2)

def rsvpno(request, event_id, user_id):
	return dorsvp(request, event_id, user_id, 4)

def rsvpremove(request, event_id, user_id):
	return dorsvp(request, event_id, user_id, 0)
