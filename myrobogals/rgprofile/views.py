from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from myrobogals.auth.models import User, Group, MemberStatus, MemberStatusType
from myrobogals.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from myrobogals.rgprofile.models import Position, UserList
from myrobogals.rgprofile.usermodels import University
from myrobogals.auth import authenticate, login
#from django.forms.validators import email_re
from django import forms
from django.utils.translation import ugettext_lazy as _
from myrobogals.rgmain.utils import SelectDateWidget
import datetime
import re
from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.db.models import Q
from myrobogals.admin.widgets import FilteredSelectMultiple

def joinstart(request):
	if request.user.is_authenticated():
		return render_to_response('join_already_logged_in.html', {}, context_instance=RequestContext(request))
	else:
		secondlevel = []
		# Get chapters whose parent = 1 (Robogals Global)
		superchapters = Group.objects.filter(parent_id=1)
		for superchapter in superchapters:
			chapters = Group.objects.filter(parent=superchapter)
			t = loader.get_template('chapter_listing_sub.html')
			c = Context({
				'superchapter': superchapter,
				'chapters': chapters,
			})
			secondlevel.append(t.render(c))
		return render_to_response('join_select_chapter.html', {'secondlevels': secondlevel}, context_instance=RequestContext(request))

def joinchapter(request, chapterurl):
	chapter = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if request.user.is_authenticated():
		return render_to_response('join_already_logged_in.html', {}, context_instance=RequestContext(request))
	else:
		if chapter.is_joinable:
			return edituser(request, '', chapter)
		else:
			raise Http404  # can't join this chapter

@login_required
def viewlist(request, chapterurl, list_id):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter())):
		l = get_object_or_404(UserList, pk=list_id, chapter=c)
		users = l.users
		search = ''
		if 'search' in request.GET:
			search = request.GET['search']
			users = users.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(mobile__icontains=search))
		users = users.order_by('last_name', 'first_name')
		return render_to_response('list_user_list.html', {'userlist': l, 'list_id': list_id, 'users': users, 'search': search, 'chapter': c, 'return': request.path + '?' + request.META['QUERY_STRING']}, context_instance=RequestContext(request))
	else:
		raise Http404

class EmailModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.last_name + ", " + obj.first_name

class EditListForm(forms.Form):
	name = forms.CharField(max_length=256)
	users = EmailModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple("Members", False, attrs={'rows': 20}), required=True)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		super(EditListForm, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['users'].queryset = User.objects.filter(is_active=True).order_by('last_name')
		else:
			self.fields['users'].queryset = User.objects.filter(groups=user.chapter(), is_active=True).order_by('last_name')

@login_required
def listuserlists(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	uls = UserList.objects.filter(chapter=c)
	return render_to_response('list_user_lists.html', {'uls': uls, 'chapter': c}, context_instance=RequestContext(request))

@login_required
def adduserlist(request, chapterurl):
	return edituserlist(request, chapterurl, 0)

@login_required
def edituserlist(request, chapterurl, list_id):
	if list_id == 0:
		new = True
	else:
		new = False
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter())):
		if new:
			l = UserList()
		else:
			l = get_object_or_404(UserList, pk=list_id, chapter=c)
		if request.method == 'POST':
			ulform = EditListForm(request.POST, user=request.user)
			if ulform.is_valid():
				data = ulform.cleaned_data
				l.name = data['name']
				if new:
					l.chapter = c
					l.save()
				l.users = data['users']
				l.save()
				return HttpResponseRedirect('/chapters/' + chapterurl + '/lists/' + str(l.pk) + '/')
		else:
			if new:
				ulform = EditListForm(None, user=request.user)
			else:
				users_selected = []
				for u in l.users.all():
					users_selected.append(u.pk)
				ulform = EditListForm({
					'name': l.name,
					'users': users_selected}, user=request.user)
		return render_to_response('edit_user_list.html', {'new': new, 'userlist': l, 'ulform': ulform, 'list_id': list_id, 'chapter': c}, context_instance=RequestContext(request))

@login_required
def editusers(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter())):
		users = User.objects.filter(groups=c)
		search = ''
		if 'search' in request.GET:
			search = request.GET['search']
			users = users.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(mobile__icontains=search))
		users = users.order_by('last_name', 'first_name')
		return render_to_response('user_list.html', {'users': users, 'search': search, 'chapter': c, 'return': request.path + '?' + request.META['QUERY_STRING']}, context_instance=RequestContext(request))
	else:
		raise Http404

@login_required
def adduser(request, chapterurl):
	chapter = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	return edituser(request, '', chapter)

@login_required
def redirtoself(request):
	return HttpResponseRedirect("/profile/" + request.user.username + "/")

@login_required
def redirtoeditself(request):
	return HttpResponseRedirect("/profile/" + request.user.username + "/edit/")

def detail(request, username):
	u = get_object_or_404(User, username__exact=username)
	current_positions = Position.objects.filter(user=u, position_date_end__isnull=True)
	past_positions = Position.objects.filter(user=u, position_date_end__isnull=False)
	if u.membertype().type_of_person == 1:  # Student
		show_course = True
	else:
		show_course = False
	if u.membertype().type_of_person == 2:  # Industry
		show_job = True
	else:
		show_job = False
	return render_to_response('profile_view.html', {'user': u, 'current_positions': current_positions, 'past_positions': past_positions, 'show_course': show_course, 'show_job': show_job}, context_instance=RequestContext(request))


# Widget that shows a month and year field only
RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')
class SelectMonthYearWidget(Widget):
	none_value = ('0', '---')
	month_field = '%s_month'
	year_field = '%s_year'

	def __init__(self, attrs=None, years=None, required=True):
		# years is an optional list/tuple of years to use in the "year" select box.
		self.attrs = attrs or {}
		self.required = required
		if years:
			self.years = years
		else:
			this_year = datetime.date.today().year
			self.years = range(this_year-10, this_year+10)

	def render(self, name, value, attrs=None):
		try:
			year_val, month_val = value.year, value.month
		except AttributeError:
			year_val = month_val = None
			if isinstance(value, basestring):
				match = RE_DATE.match(value)
				if match:
					year_val, month_val, day_val = [int(v) for v in match.groups()]

		output = []

		if 'id' in self.attrs:
			id_ = self.attrs['id']
		else:
			id_ = 'id_%s' % name

		local_attrs = self.build_attrs(id=self.month_field % id_)
		month_choices = MONTHS.items()
		month_choices.insert(0, self.none_value)
		#month_choices.sort()
		s = Select(choices=month_choices)
		select_html = s.render(self.month_field % name, month_val, local_attrs)
		output.append(select_html)

		year_choices = [(i, i) for i in self.years]
		year_choices.insert(0, self.none_value)
		local_attrs['id'] = self.year_field % id_
		s = Select(choices=year_choices)
		select_html = s.render(self.year_field % name, year_val, local_attrs)
		output.append(select_html)

		return mark_safe(u'\n'.join(output))

	def id_for_label(self, id_):
		return '%s_month' % id_
	id_for_label = classmethod(id_for_label)

	def value_from_datadict(self, data, files, name):
		y = data.get(self.year_field % name)
		m = data.get(self.month_field % name)
		d = "01"
		if y == m == "0":
			return None
		if y and m:
			return '%s-%s-%s' % (y, m, d)
		return data.get(name, None)

# Personal information
class FormPartOne(forms.Form):
	GENDERS = (
		(1, 'Male'),
		(2, 'Female'),
	)

	first_name = forms.CharField(label=_('First name'), max_length=30)
	last_name = forms.CharField(label=_('Last name'), max_length=30)
	email = forms.EmailField(label=_('Email'), max_length=64)
	alt_email = forms.EmailField(label=_('Alternate email'), max_length=64, required=False)
	mobile = forms.CharField(label=_('Mobile phone'), max_length=20)
	gender = forms.ChoiceField(choices=GENDERS, initial=2)

# Privacy settings
class FormPartTwo(forms.Form):
	PRIVACY_CHOICES = (
		(20, _('Everyone (the whole internet)')),
		(10, _('Only Robogals members')),
		(5, _('Only Robogals members in my chapter')),
		(0, _('Only committee')),
	)

	privacy = forms.ChoiceField(label=_('Who can see my profile?'), choices=PRIVACY_CHOICES, initial=5)
	dob_public = forms.BooleanField(label=_('Show date of birth in my profile'), required=False)
	email_public = forms.BooleanField(label=_('Show email address in my profile'), required=False)

# Demographic information
class FormPartThree(forms.Form):
	dob = forms.DateField(label=_('Date of birth'), widget=SelectDateWidget(), required=False)
	course = forms.CharField(label=_('Course'), max_length=128, required=False)
	uni_start = forms.DateField(label=_('Started university'), widget=SelectMonthYearWidget(), required=False)
	uni_end = forms.DateField(label=_('Will finish university'), widget=SelectMonthYearWidget(), required=False)
	university = forms.ModelChoiceField(queryset=University.objects.all(), required=False)
	#job_title = forms.CharField(_('Job title'), max_length=128, required=False)
	#company = forms.CharField(_('Company'), max_length=128, required=False)

# User preferences
class FormPartFour(forms.Form):
	email_reminder_optin = forms.BooleanField(label=_('Allow email reminders about my upcoming school visits'), initial=True, required=False)
	mobile_reminder_optin = forms.BooleanField(label=_('Allow SMS reminders about my upcoming school visits'), initial=True, required=False)
	email_chapter_optin = forms.BooleanField(label=_('Allow my local Robogals chapter to send me email updates'), initial=True, required=False)
	mobile_marketing_optin = forms.BooleanField(label=_('Allow my local Robogals chapter to send me SMS updates'), initial=True, required=False)
	email_newsletter_optin = forms.BooleanField(label=_('Subscribe to The Amplifier, the monthly email newsletter of Robogals Global'), initial=True, required=False)

def edituser(request, username, chapter=None):
	pwerr = ''
	usererr = ''
	new_username = ''
	if username == '':
		join = True
		u = User()
		if request.user.is_superuser or (request.user.is_staff and request.user.chapter() == chapter):
			adduser = True
		else:
			adduser = False
	else:
		join = False
		adduser = False
		if not request.user.is_authenticated():
			return HttpResponseRedirect("/login/?next=/profile/edit/")
		u = get_object_or_404(User, username__exact=username)
		chapter = u.chapter()
	if join or request.user.is_superuser or request.user.id == u.id or (request.user.is_staff and request.user.chapter() == u.chapter()):
		if request.method == 'POST':
			if join:
				new_username = request.POST['username'].strip()
			formpart1 = FormPartOne(request.POST)
			formpart2 = FormPartTwo(request.POST)
			formpart3 = FormPartThree(request.POST)
			formpart4 = FormPartFour(request.POST)
			if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid() and formpart4.is_valid():
				if join:
					username_len = len(new_username)
					if username_len < 3:
						usererr = _('Your username must be 3 or more characters')
					elif username_len > 30:
						usererr = _('Your username must be less than 30 characters')
					else:
						try:
							usercheck = User.objects.get(username=new_username)
						except User.DoesNotExist:
							if request.POST['password1'] == request.POST['password2']:
								if len(request.POST['password1']) < 5:
									pwerr = _('Your password must be at least 5 characters long')
								else:
									u = User.objects.create_user(new_username, '', request.POST['password1'])
									u.groups.add(chapter)
									mt = MemberStatus(user_id=u.pk, statusType_id=1)
									mt.save()
							else:
								pwerr = _('The password and repeated password did not match. Please try again')
						else:
							usererr = _('That username is already taken')
				if request.user.is_staff and request.user != u:
					if len(request.POST['password1']) > 0:
						if request.POST['password1'] == request.POST['password2']:
							u.set_password(request.POST['password1'])
						else:
							pwerr = _('The password and repeated password did not match. Please try again')
				if pwerr == '' and usererr == '':
					data = formpart1.cleaned_data
					u.first_name = data['first_name']
					u.last_name = data['last_name']
					u.email = data['email']
					u.alt_email = data['alt_email']
					u.mobile = data['mobile']
					u.gender = data['gender']
					data = formpart2.cleaned_data
					u.privacy = data['privacy']
					u.dob_public = data['dob_public']
					u.email_public = data['email_public']
					data = formpart3.cleaned_data
					u.dob = data['dob']
					u.course = data['course']
					u.uni_start = data['uni_start']
					u.uni_end = data['uni_end']
					u.university = data['university']
					#u.job_title = data['job_title']
					#u.company = data['company']
					data = formpart4.cleaned_data
					u.email_reminder_optin = data['email_reminder_optin']
					u.email_chapter_optin = data['email_chapter_optin']
					u.mobile_reminder_optin = data['mobile_reminder_optin']
					u.mobile_marketing_optin = data['mobile_marketing_optin']
					u.email_newsletter_optin = data['email_newsletter_optin']
					if join:
						u.is_active = True
						u.is_staff = False
						u.is_superuser = False
					u.save()
					if 'return' in request.POST:
						return HttpResponseRedirect(request.POST['return'])
					elif join:
						return HttpResponseRedirect("/welcome/" + chapter.myrobogals_url + "/")
					else:
						return HttpResponseRedirect("/profile/" + username + "/")
		else:
			if join:
				formpart1 = FormPartOne()
				formpart2 = FormPartTwo()
				formpart3 = FormPartThree()
				formpart4 = FormPartFour()
			else:
				formpart1 = FormPartOne({
					'first_name': u.first_name,
					'last_name': u.last_name,
					'email': u.email,
					'alt_email': u.alt_email,
					'mobile': u.mobile,
					'gender': u.gender})
				formpart2 = FormPartTwo({
					'privacy': u.privacy,
					'dob_public': u.dob_public,
					'email_public': u.email_public})
				if u.university:
					uni = u.university.pk
				else:
					uni = None
				formpart3 = FormPartThree({
					'dob': u.dob,
					'course': u.course,
					'uni_start': u.uni_start,
					'uni_end': u.uni_end,
					'university': uni,
					'job_title': u.job_title,
					'company': u.company})
				formpart4 = FormPartFour({
					'email_reminder_optin': u.email_reminder_optin,
					'email_chapter_optin': u.email_chapter_optin,
					'mobile_reminder_optin': u.mobile_reminder_optin,
					'mobile_marketing_optin': u.mobile_marketing_optin,
					'email_newsletter_optin': u.email_newsletter_optin})
		if 'return' in request.GET:
			return_url = request.GET['return']
		elif 'return' in request.POST:
			return_url = request.POST['return']
		else:
			return_url = ''

		chpass = (join or (request.user.is_staff and request.user != u))			
		return render_to_response('profile_edit.html', {'join': join, 'adduser': adduser, 'chpass': chpass, 'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3, 'formpart4': formpart4, 'u': u, 'chapter': chapter, 'usererr': usererr, 'pwerr': pwerr, 'new_username': new_username, 'return': return_url}, context_instance=RequestContext(request))
	else:
		raise Http404  # don't have permission to change

def show_login(request):
	try:
		next = request.POST['next']
	except KeyError:
		try:
			next = request.GET['next']
		except KeyError:
			next = '/'
	return render_to_response('login_form.html', {'next': next}, context_instance=RequestContext(request))

def process_login(request):
	if request.method != 'POST':
		return HttpResponseRedirect('/login/')
#   if email_re.match(username)
	username = request.POST['username']
	password = request.POST['password']
	try:
		next = request.POST['next']
	except KeyError:
		try:
			next = request.GET['next']
		except KeyError:
			next = '/'
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			return HttpResponseRedirect(next)
		else:
			return render_to_response('login_form.html', {'username': username, 'error': 'Your account has been disabled', 'next': next}, context_instance=RequestContext(request))
	else:
		return render_to_response('login_form.html', {'username': username, 'error': 'Invalid username or password', 'next': next}, context_instance=RequestContext(request))

def password_change_done(request):
	return render_to_response('password_change_done.html', {}, context_instance=RequestContext(request))
