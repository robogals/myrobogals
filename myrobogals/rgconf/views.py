from django.shortcuts import render_to_response, get_object_or_404
from myrobogals.auth.models import User
from myrobogals.auth.decorators import login_required
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django import forms
from django.utils.translation import ugettext_lazy as _
from myrobogals.rgmain.utils import SelectDateWidget
from myrobogals.rgconf.models import Conference, ConferenceAttendee, ConferencePart
from django.core.urlresolvers import reverse
from myrobogals.rgchapter.models import ShirtSize
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient
from myrobogals.rgteaching.views import EmailModelMultipleChoiceField
from myrobogals.admin.widgets import FilteredSelectMultiple
from tinymce.widgets import TinyMCE
import re
from datetime import datetime, timedelta

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

	def clean(self):
		cleaned_data = self.cleaned_data
		attendee_type = int(cleaned_data.get('attendee_type'))
		outgoing_position = cleaned_data.get('outgoing_position')
		incoming_position = cleaned_data.get('incoming_position')
		print attendee_type
		print outgoing_position
		print incoming_position
		if attendee_type == 0:
			if not outgoing_position:
				raise forms.ValidationError(_('You have indicated that you are outgoing from your chapter committee, but did not specify your outgoing position. Please state the position from which you are outgoing, e.g. "Schools Manager". If your chapter does not assign specific roles, you can simply put "General Committee"'))
		elif attendee_type == 1:
			if not incoming_position:
				raise forms.ValidationError(_('You have indicated that you are continuing in your chapter committee, but did not specify your position. Please state the position in which you are continuing, e.g. "Schools Manager". If your chapter does not assign specific roles, you can simply put "General Committee"'))
		elif attendee_type == 2:
			if not incoming_position:
				raise forms.ValidationError(_('You have indicated that you are incoming into your chapter committee, but did not specify your incoming position. Please state the position into which you are incoming, e.g. "Schools Manager". If your chapter does not assign specific roles, you can simply put "General Committee"'))
		return cleaned_data

	GENDERS = (
		(1, 'Male'),
		(2, 'Female'),
	)

	first_name = forms.CharField(label=_("First name"), help_text=_("Whatever you put here is what the name tag will show.<br />You can put a preferred name, e.g. 'Bec' instead of 'Rebecca' if you like."), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	last_name = forms.CharField(label=_("Last name"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	attendee_type = forms.ChoiceField(label=_("This person is"), choices=((0,''),))
	gender = forms.ChoiceField(label=_("Gender"), choices=GENDERS)
	outgoing_position = forms.CharField(label=_("Outgoing position"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	incoming_position = forms.CharField(label=_("Incoming position"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	mobile = forms.CharField(label=_("Mobile/cell phone"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	dob = forms.DateField(label=_("Date of birth"), help_text=_("If you are under 18, we will send you a form that must be signed by your parent or guardian."), widget=SelectDateWidget(), required=True)
	update_account = forms.BooleanField(label=_("Also update this person's account in myRobogals with the email, mobile and DOB above"), required=False, initial=False)
	emergency_name = forms.CharField(label=_("Contact name"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	emergency_number = forms.CharField(label=_("Contact number"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	emergency_relationship = forms.CharField(label=_("Relationship to you"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
	tshirt = forms.ModelChoiceField(label=_("T-shirt size"), queryset=ShirtSize.objects.filter(chapter__id=1), required=True)
	arrival_time = forms.CharField(label=_("Arrival time, if known"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	dietary_reqs = forms.CharField(label=_("Dietary requirements"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	comments = forms.CharField(label=_("Comments or special requests"), required=False, widget=forms.TextInput(attrs={'size': '30'}))

@login_required
def editrsvp(request, conf_id, username):
	chapter = request.user.chapter
	if not request.user.is_staff:
		if request.user.username != username:
			raise Http404
	u = get_object_or_404(User, username=username)
	if u.chapter != chapter:
		if not request.user.is_superuser:
			raise Http404
	conf = get_object_or_404(Conference, pk=conf_id)
	if conf.is_hidden():
		raise Http404
	if not conf.is_open():
		return render_to_response('response.html', {'msg': conf.closed_msg, 'msgtitle': _('Registration is closed')}, context_instance=RequestContext(request))
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
			elif ca.balance_owing()[1] == None:
				return HttpResponseRedirect('/profile/' + u.username + '/')
			elif ca.balance_owing()[0] > 0.0:
				return HttpResponseRedirect('/conferences/' + str(conf_id) + '/' + u.username + '/invoice/')
			else:
				return HttpResponseRedirect('/profile/' + u.username + '/')
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
	customtotals = [0,0,0,0,0]
	accommtotals = {}
	accommtotals_sorted = []
	accommtotals_numnights = {}
	accommtotals_numnights_sorted = []
	if request.user.is_superuser:
		one_day = timedelta(days=1)
		for ca in cas:
			for i in range(5):
				if getattr(ca, "custom" + str(i+1)):
					customtotals[i] += 1
			if ca.check_in and ca.check_out:
				curdate = ca.check_in
				while curdate != ca.check_out:
					if not curdate in accommtotals:
						accommtotals[curdate] = [0,0,0,0]
					accommtotals[curdate][int(ca.gender)] += 1
					accommtotals[curdate][3] += 1
					curdate += one_day
				nights = ca.check_out - ca.check_in
				if not nights.days in accommtotals_numnights:
					accommtotals_numnights[nights.days] = [0,0,0,0]
				accommtotals_numnights[nights.days][int(ca.gender)] += 1
				accommtotals_numnights[nights.days][3] += 1
		accommtotals_sorted = sorted(accommtotals.items(), key=lambda totals: totals[0])
		accommtotals_numnights_sorted = sorted(accommtotals_numnights.items(), key=lambda totals: totals[0])
	if (not conf.custom1_setting) and (not conf.custom2_setting) and (not conf.custom3_setting) and (not conf.custom4_setting) and (not conf.custom5_setting):
		hide_all_custom = True
	else:
		hide_all_custom = False
	return render_to_response(template_file, {'conf': conf, 'chapter': chapter, 'cas': cas, 'customtotals': customtotals, 'accommtotals': accommtotals_sorted, 'accommtotals_nights': accommtotals_numnights_sorted, 'hide_all_custom': hide_all_custom}, context_instance=RequestContext(request))

class EmailAttendeesForm(forms.Form):
	# Set up form
	from_type = forms.ChoiceField(choices=((0,"Robogals"),(1,_("Chapter name")),(2,_("Your name"))), initial=1)
	subject = forms.CharField(max_length=256, required=False)
	body = forms.CharField(widget=TinyMCE(attrs={'cols': 70}), required=False)
	memberselect = EmailModelMultipleChoiceField(queryset=ConferenceAttendee.objects.none(), widget=FilteredSelectMultiple(_("Recipients"), False, attrs={'rows': 10}), required=False)

	def __init__(self, *args, **kwargs):
		# Grab params, clear scope
		user=kwargs['user']
		del kwargs['user']
		conf=kwargs['conference']
		del kwargs['conference']
		
		super(EmailAttendeesForm, self).__init__(*args, **kwargs)
		
		# "From" field
		self.fields['from_type'].choices = (
			(0, "Robogals <" + user.email + ">"),
			(1, user.chapter.name + " <" + user.email + ">"),
			(2, user.get_full_name() + " <" + user.email + ">")
		)
		
		# Using `ConferenceAttendee`
		self.fields['memberselect'].queryset = ConferenceAttendee.objects.filter(conference=conf.id).order_by('last_name')
		
		# Using `User`
		# id_list = ConferenceAttendee.objects.filter(conference=conf.id).values_list('user_id')
		# self.fields['memberselect'].queryset = User.objects.filter(id__in = id_list, is_active=True, email_reminder_optin=True).order_by('last_name')
	
@login_required
def rsvpemail(request, conf_id):
	# Superuser check
	if not request.user.is_superuser:
		raise Http404
    
	conf = get_object_or_404(Conference, pk=conf_id)
	chapter = request.user.chapter
	
	# Determine if form has been POSTed back
	if request.method == 'POST':
		# Validate email form data
		emailform = EmailAttendeesForm(request.POST, conference=conf, user=request.user)
		if emailform.is_valid():
			data = emailform.cleaned_data
			
			# Set up message
			message = EmailMessage()
			message.subject = data['subject']
			message.body = data['body']
			message.from_address = request.user.email
			message.reply_address = request.user.email
			message.sender = request.user
			message.html = True
			
			if int(data['from_type']) == 0:
				message.from_name = "Robogals"
			elif int(data['from_type']) == 1:
				message.from_name = request.user.chapter.name
			else:
				message.from_name = request.user.get_full_name()
				
			message.scheduled = False
				
			# Don't send it yet until the recipient list is done
			message.status = -1
			# Save to database so we get a value for the primary key,
			# which we need for entering the recipient entries
			message.save()
			
			
			# Start processing recipient list
			# Insert choices for attending, not attending etc here
			if request.POST['invitee_type'] == '1':	# All
				# Using `ConferenceAttendee`
				users = ConferenceAttendee.objects.filter(conference=conf.id)
		
				# Using `User`
				# id_list = ConferenceAttendee.objects.filter(conference=conf.id).values_list('user_id')
				# users = User.objects.filter(id__in = id_list, is_active=True, email_reminder_optin=True).order_by('last_name')
			elif request.POST['invitee_type'] == '2': # Selected
				users = data['memberselect']

			for one_user in users:
				recipient = EmailRecipient()
				recipient.message = message
				recipient.to_address = one_user.email
				
				# Using `ConferenceAttendee`
				recipient.user = one_user.user
				recipient.to_name = one_user.full_name()
				
				# Using `User`
				# recipient.user = one_user
				# recipient.to_name = one_user.get_full_name()

				recipient.save()
			
			# Send message
			message.status = 0
			message.save()
			
			request.user.message_set.create(message=unicode(_("Email sent successfully")))
			return HttpResponseRedirect('/conferences/' + str(conf.pk) + '/')
	else:
		emailform = EmailAttendeesForm(None, conference=conf, user=request.user)
	
	
	# Display email form
	return render_to_response('conf_rsvp_email.html', {'conf': conf, 'emailform': emailform}, context_instance=RequestContext(request))

@login_required
def showinvoice(request, conf_id, username):
	chapter = request.user.chapter
	if not request.user.is_staff:
		if request.user.username != username:
			raise Http404
	conf = get_object_or_404(Conference, pk=conf_id)
	if not conf.enable_invoicing:
		raise Http404
	u = get_object_or_404(User, username=username)
	if u.chapter != chapter:
		if not request.user.is_superuser:
			raise Http404
	try:
		ca = ConferenceAttendee.objects.get(conference=conf, user=u)
	except ConferenceAttendee.DoesNotExist:
		raise Http404
	return render_to_response('conf_invoice.html', {'conf': conf, 'chapter': chapter, 'ca': ca, 'user': u}, context_instance=RequestContext(request))

@login_required
def nametagscsv(request, conf_id):
	if not request.user.is_superuser:
		raise Http404
	conf = get_object_or_404(Conference, pk=conf_id)
	cas = ConferenceAttendee.objects.filter(conference=conf).order_by('user__chapter', 'last_name')
	response = HttpResponse(mimetype='text/csv')
	filename = 'robogals-sine-nametags-' + str(datetime.now().date()) + '.csv'
	response['Content-Disposition'] = 'attachment; filename=' + filename
	t = loader.get_template('conf_nametags_csv.txt')
	c = Context({'cas': cas})
	response.write(t.render(c))
	return response
