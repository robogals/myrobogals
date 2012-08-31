from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from myrobogals.auth.models import User
from myrobogals.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django import forms
from django.utils.translation import ugettext_lazy as _
from myrobogals.rgmain.utils import SelectDateWidget
from myrobogals.rgconf.models import Conference, ConferenceAttendee, ConferencePart
from django.core.urlresolvers import reverse
from myrobogals.rgchapter.models import ShirtSize
import re
from datetime import datetime

@login_required
def home(request):
	confs = Conference.objects.all()
	return render_to_response('conf_home.html', {'confs': confs}, context_instance=RequestContext(request))

class ConfRSVPForm(forms.Form):
	def __init__(self, *args, **kwargs):
		conf=kwargs['conf']
		del kwargs['conf']
		user=kwargs['user']
		del kwargs['user']
		super(ConfRSVPForm, self).__init__(*args, **kwargs)
		this_year = str(conf.committee_year)
		last_year = str(conf.committee_year - 1)
		next_year = str(conf.committee_year + 1)
		CHOICES = (
			(0, last_year + "/" + this_year + " committee, now outgoing"),
			(1, last_year + "/" + this_year + " committee, continuing into " + this_year + "/" + next_year + " committee"),
			(2, "Incoming into " + this_year + "/" + next_year + " committee"),
			(3, "None of the above; ordinary volunteer")
		)
		self.fields['attendee_type'].choices = CHOICES
		self.fields['first_name'].initial = user.first_name
		self.fields['last_name'].initial = user.last_name
		self.fields['email'].initial = user.email
		if user.mobile == '':
			pass
		elif user.mobile[0] != '0':
			self.fields['mobile'].initial = '+' + user.mobile
		else:
			self.fields['mobile'].initial = user.mobile			
		self.fields['dob'].initial = user.dob
		if user.gender in [1, 2]:
			self.fields['gender'].initial = user.gender
		else:
			self.fields['gender'].initial = 2		
	
	GENDERS = (
		(1, 'Male'),
		(2, 'Female'),
	)

	first_name = forms.CharField(label=_("First name"), help_text=_("Whatever you put here is what this person's name tag will show.<br />You can put a preferred name, e.g. 'Bec' instead of 'Rebecca' if you like."), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	last_name = forms.CharField(label=_("Last name"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	attendee_type = forms.ChoiceField(label=_("This person is"), choices=((0,''),))
	gender = forms.ChoiceField(label=_("Gender"), choices=GENDERS)
	outgoing_position = forms.CharField(label=_("Outgoing position"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	incoming_position = forms.CharField(label=_("Incoming position"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	mobile = forms.CharField(label=_("Mobile"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	dob = forms.DateField(label=_("Date of birth"), widget=SelectDateWidget(), required=True)
	update_account = forms.BooleanField(label=_("Also update this person's account in myRobogals with the email, mobile and DOB above"), required=False, initial=False)
	emergency_name = forms.CharField(label=_("Contact name"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	emergency_number = forms.CharField(label=_("Contact number"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	emergency_relationship = forms.CharField(label=_("Relationship to you"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	tshirt = forms.ModelChoiceField(label=_("T-shirt size"), queryset=ShirtSize.objects.filter(chapter__id=1), required=True)
	arrival_time = forms.CharField(label=_("Flight arrival time, if known"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	dietary_reqs = forms.CharField(label=_("Dietary requirements"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	comments = forms.CharField(label=_("Comments or special requests"), required=False, widget=forms.TextInput(attrs={'size': '30'}))

@login_required
def editrsvp(request, conf_id, username):
	chapter = request.user.chapter
	if not request.user.is_staff:
		if request.user.username != username:
			raise Http404
	conf = get_object_or_404(Conference, pk=conf_id)
	u = get_object_or_404(User, username=username)
	if u.chapter != chapter:
		if not request.user.is_superuser:
			raise Http404
	try:
		ca = ConferenceAttendee.objects.get(conference=conf, user=u)
		new = False
	except ConferenceAttendee.DoesNotExist:
		ca = ConferenceAttendee()
		ca.rsvp_time = datetime.now()
		new = True
	if request.method == 'POST':
		form = ConfRSVPForm(request.POST, conf=conf, user=u)
		if form.is_valid():
			if new:
				ca.user = u
				ca.conference = conf
			data = form.cleaned_data
			ca.first_name = data['first_name']
			ca.last_name = data['last_name']
			ca.attendee_type = data['attendee_type']
			ca.outgoing_position = data['outgoing_position']
			ca.incoming_position = data['incoming_position']
			ca.email = data['email']
			ca.mobile = data['mobile']
			ca.dob = data['dob']
			ca.gender = data['gender']
			ca.emergency_name = data['emergency_name']
			ca.emergency_number = data['emergency_number']
			ca.emergency_relationship = data['emergency_relationship']
			ca.tshirt = data['tshirt']
			ca.arrival_time = data['arrival_time']
			ca.dietary_reqs = data['dietary_reqs']
			ca.comments = data['comments']
			ca.save()
			ca.parts_attending.clear()
			for postkey, postval in request.POST.items():
				m = re.match(r"^part(?P<part_id>\d+)$", postkey)
				if m:
					part_id = int(m.groupdict()['part_id'])
					if postval == '1':
						try:
							part = ConferencePart.objects.get(pk=part_id, conference=conf)
							ca.parts_attending.add(part)
						except ConferencePart.DoesNotExist:
							pass
			ca.save()
			request.user.message_set.create(message=unicode(_("Conference RSVP saved")))
			if data['update_account']:
				u.email = data['email']
				u.dob = data['dob']
				u.mobile = data['mobile']
				u.gender = data['gender']
				u.save()
				request.user.message_set.create(message=unicode(_("Member account updated with new details")))
			if request.user.is_staff:
				return HttpResponseRedirect('/conferences/' + str(conf_id) + '/')
			else:
				return HttpResponseRedirect('/conferences/' + str(conf_id) + '/' + u.username + '/invoice/')
	else:
		if new:
			form = ConfRSVPForm(None, conf=conf, user=u)
		else:
			form = ConfRSVPForm({
					'first_name': ca.first_name,
					'last_name': ca.last_name,
					'attendee_type': ca.attendee_type,
					'outgoing_position': ca.outgoing_position,
					'incoming_position': ca.incoming_position,
					'email': ca.email,
					'mobile': ca.mobile,
					'dob': ca.dob,
					'gender': ca.gender,
					'emergency_name': ca.emergency_name,
					'emergency_number': ca.emergency_number,
					'emergency_relationship': ca.emergency_relationship,
					'tshirt': ca.tshirt,
					'arrival_time': ca.arrival_time,
					'dietary_reqs': ca.dietary_reqs,
					'comments': ca.comments}, conf=conf, user=u)

	all_parts = ConferencePart.objects.filter(conference=conf)
	if ca.pk:
		sel_parts = ca.parts_attending.all().values_list('pk', flat=True)
	else:
		sel_parts = []
	return render_to_response('conf_rsvp_edit.html', {'new': new, 'form': form, 'conf_id': conf_id, 'username': username, 'u': u, 'conf': conf, 'all_parts': all_parts, 'sel_parts': sel_parts}, context_instance=RequestContext(request))

@login_required
def rsvplist(request, conf_id):
	if not request.user.is_staff:
		return HttpResponseRedirect('/conferences/' + str(conf_id) + '/' + request.user.username + '/rsvp/')
	conf = get_object_or_404(Conference, pk=conf_id)
	chapter = request.user.chapter
	if 'username' in request.GET:
		try:
			u = User.objects.get(username=request.GET['username'])
			if request.user.is_superuser or u.chapter == chapter:
				return HttpResponseRedirect('/conferences/' + str(conf_id) + '/' + u.username + '/rsvp/')
			else:
				raise User.DoesNotExist
		except User.DoesNotExist:
			request.user.message_set.create(message=unicode(_("- No such username exists in your chapter")))
	if request.user.is_superuser:
		cas = ConferenceAttendee.objects.filter(conference=conf).order_by('user__chapter', 'last_name')
	else:
		cas = ConferenceAttendee.objects.filter(user__chapter=chapter, conference=conf)
	template_file = 'conf_rsvp_list.html'
	if 'accomm' in request.GET:
		if int(request.GET['accomm']) == 1:
			if request.user.is_superuser:
				template_file = 'conf_accomm_list.html'
	return render_to_response(template_file, {'conf': conf, 'chapter': chapter, 'cas': cas}, context_instance=RequestContext(request))

@login_required
def showinvoice(request, conf_id, username):
	chapter = request.user.chapter
	if not request.user.is_staff:
		if request.user.username != username:
			raise Http404
	conf = get_object_or_404(Conference, pk=conf_id)
	u = get_object_or_404(User, username=username)
	if u.chapter != chapter:
		if not request.user.is_superuser:
			raise Http404
	try:
		ca = ConferenceAttendee.objects.get(conference=conf, user=u)
	except ConferenceAttendee.DoesNotExist:
		raise Http404
	return render_to_response('conf_invoice.html', {'conf': conf, 'chapter': chapter, 'ca': ca, 'user': u}, context_instance=RequestContext(request))
