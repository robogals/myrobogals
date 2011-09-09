from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from myrobogals.auth.models import User, Group, MemberStatus, MemberStatusType
from myrobogals.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from myrobogals.rgprofile.models import Position, UserList
from myrobogals.rgmain.models import University, MobileRegex
from myrobogals.auth import authenticate, login
#from django.forms.validators import email_re
from django import forms
from django.utils.translation import ugettext_lazy as _
from myrobogals.rgmain.utils import SelectDateWidget
import datetime
import re
from django.forms.widgets import Widget, Select, TextInput
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.db.models import Q
from myrobogals.admin.widgets import FilteredSelectMultiple
from myrobogals.settings import MEDIA_ROOT
from time import time
import csv
from myrobogals.rgprofile.functions import importcsv, genandsendpw, RgImportCsvException, RgGenAndSendPwException
from myrobogals.rgchapter.models import DisplayColumn, ShirtSize
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient
from django.forms.fields import email_re

'''
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
'''

def joinchapter(request, chapterurl):
	chapter = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if chapter.is_joinable:
		if request.user.is_authenticated():
			return render_to_response('join_already_logged_in.html', {}, context_instance=RequestContext(request))
		else:
			return edituser(request, '', chapter)
	else:
		join_page = chapter.join_page.format(chapter=chapter)
		return render_to_response('joininfo.html', {'chapter': chapter, 'join_page': join_page}, context_instance=RequestContext(request))

@login_required
def viewlist(request, chapterurl, list_id):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		l = get_object_or_404(UserList, pk=list_id, chapter=c)
		users = l.users
		search = ''
		if 'search' in request.GET:
			search = request.GET['search']
			users = users.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(mobile__icontains=search))
		users = users.order_by('last_name', 'first_name')
		display_columns = l.display_columns.all()
		return render_to_response('list_user_list.html', {'userlist': l, 'list_id': list_id, 'users': users, 'search': search, 'chapter': c, 'display_columns': display_columns, 'return': request.path + '?' + request.META['QUERY_STRING']}, context_instance=RequestContext(request))
	else:
		raise Http404

class EmailModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.last_name + ", " + obj.first_name

class DPModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.display_name_en

class EditListForm(forms.Form):
	name = forms.CharField(max_length=256)
	users = EmailModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple(_("Members"), False, attrs={'rows': 20}), required=True)
	display_columns = DPModelMultipleChoiceField(queryset=DisplayColumn.objects.all().order_by('display_name_en'), label=_("Columns to display"), widget=FilteredSelectMultiple(_("Columns"), False, attrs={'rows': 10}), required=True, initial=(26,4,15))
	notes = forms.CharField(required=False, widget=forms.Textarea)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		super(EditListForm, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['users'].queryset = User.objects.filter(is_active=True).order_by('last_name')
		else:
			self.fields['users'].queryset = User.objects.filter(chapter=user.chapter, is_active=True).order_by('last_name')

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
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		if new:
			l = UserList()
		else:
			l = get_object_or_404(UserList, pk=list_id, chapter=c)
		if request.method == 'POST':
			ulform = EditListForm(request.POST, user=request.user)
			if ulform.is_valid():
				data = ulform.cleaned_data
				l.name = data['name']
				l.notes = data['notes']
				if new:
					l.chapter = c
					l.save()
				l.users = data['users']
				l.display_columns = data['display_columns']
				l.save()
				request.user.message_set.create(message=unicode(_("User list \"" + l.name + "\" has been updated")))
				return HttpResponseRedirect('/chapters/' + chapterurl + '/lists/' + str(l.pk) + '/')
		else:
			if new:
				ulform = EditListForm(None, user=request.user)
			else:
				users_selected = []
				for u in l.users.all():
					users_selected.append(u.pk)
				cols_selected = []
				for u in l.display_columns.all():
					cols_selected.append(u.pk)
				ulform = EditListForm({
					'name': l.name,
					'users': users_selected,
					'display_columns': cols_selected,
					'notes': l.notes}, user=request.user)
		return render_to_response('edit_user_list.html', {'new': new, 'userlist': l, 'ulform': ulform, 'list_id': list_id, 'chapter': c}, context_instance=RequestContext(request))

@login_required
def editusers(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		users = User.objects.filter(chapter=c)
		search = ''
		if 'search' in request.GET:
			search = request.GET['search']
			users = users.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(mobile__icontains=search))
		users = users.order_by('last_name', 'first_name')
		display_columns = c.display_columns.all()
		return render_to_response('user_list.html', {'users': users, 'search': search, 'chapter': c, 'display_columns': display_columns, 'return': request.path + '?' + request.META['QUERY_STRING']}, context_instance=RequestContext(request))
	else:
		raise Http404

@login_required
def editexecs(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		users = User.objects.filter(chapter=c).filter(is_staff = True)
		search = ''
		if 'search' in request.GET:
			search = request.GET['search']
			users = users.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(mobile__icontains=search))
		users = users.order_by('last_name', 'first_name')
		display_columns = c.display_columns.all()
		return render_to_response('exec_list.html', {'users': users, 'search': search, 'chapter': c, 'display_columns': display_columns, 'return': request.path + '?' + request.META['QUERY_STRING']}, context_instance=RequestContext(request))
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
	
	# Privacy setting
	private = False
	if u.privacy >= 20:
		pass
	elif u.privacy >= 10:
		if not request.user.is_authenticated():
			private = True
	elif u.privacy >= 5:
		if not request.user.is_authenticated():
			private = True
		elif not (request.user.chapter == u.chapter):
			private = True
	else:
		if not request.user.is_authenticated():
			private = True
		elif not (request.user.chapter == u.chapter):
			private = True
		elif not request.user.is_staff:
			private = True
	
	if request.user.is_superuser:
		private = False
	
	if private:
		return render_to_response('private.html', {}, context_instance=RequestContext(request))

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

class MobileTextInput(TextInput):
	def render(self, name, value, attrs=None):
		if value != None:
			if value[0:1] in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
				value = '+' + value
		return super(MobileTextInput, self).render(name, value, attrs)

# Custom mobile field
class MobileField(forms.CharField):
	chapter = None

	def __init__(self, *args, **kwargs):
		self.chapter=kwargs['chapter']
		del kwargs['chapter']
		super(MobileField, self).__init__(*args, **kwargs)

	# This function:
	#    - validates the number
	#    - strips leading digits
	#    - prepends the country code if needed
	def clean(self, value):
		num = value.strip().replace(' ','').replace('+','')
		if num == '':
			return ''
		regexes = MobileRegex.objects.filter(collection=self.chapter.mobile_regexes)
		try:
			for regex in regexes:
				matches = re.compile(regex.regex).findall(num)
				if matches == []:
					continue
				else:
					num = num[regex.strip_digits:]
					return regex.prepend_digits + num
			# If we got this far, then it didn't match any of the regexes
			raise forms.ValidationError(self.chapter.mobile_regexes.errmsg)
		except ValueError:
			raise forms.ValidationError(self.chapter.mobile_regexes.errmsg)

class ShirtChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.size_long

# Personal information
class FormPartOne(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(FormPartOne, self).__init__(*args, **kwargs)
		self.fields['mobile'] = MobileField(label=_('Mobile phone'), max_length=20, required=False, widget=MobileTextInput(), chapter=chapter)
		if chapter.student_number_enable:
			self.fields['student_number'].label = chapter.student_number_label
			self.fields['student_number'].required = chapter.student_number_required
		else:
			del self.fields['student_number']
		if chapter.student_union_enable:
			self.fields['union_member'].label = chapter.student_union_label
			self.fields['union_member'].required = chapter.student_union_required
		else:
			del self.fields['union_member']
		if chapter.tshirt_enable:
			self.fields['tshirt'].label = chapter.tshirt_label
			self.fields['tshirt'].required = chapter.tshirt_required
			self.fields['tshirt'].queryset = ShirtSize.objects.filter(chapter=chapter)
		else:
			del self.fields['tshirt']

	GENDERS = (
		(0, '---'),
		(1, 'Male'),
		(2, 'Female'),
	)

	first_name = forms.CharField(label=_('First name'), max_length=30)
	last_name = forms.CharField(label=_('Last name'), max_length=30)
	email = forms.EmailField(label=_('Email'), max_length=64)
	student_number = forms.CharField(max_length=32)
	union_member = forms.BooleanField()
	tshirt = ShirtChoiceField(queryset=ShirtSize.objects.none())
	alt_email = forms.EmailField(label=_('Alternate email'), max_length=64, required=False)
	mobile = forms.BooleanField()
	gender = forms.ChoiceField(choices=GENDERS, initial=2)

# Privacy settings
class FormPartTwo(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(FormPartTwo, self).__init__(*args, **kwargs)

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
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(FormPartThree, self).__init__(*args, **kwargs)
	
	COURSE_TYPE_CHOICES = (
		(0, '---'),
		(1, _('Undergraduate')),
		(2, _('Postgraduate'))
	)
	
	STUDENT_TYPE_CHOICES = (
		(0, '---'),
		(1, _('Local')),
		(2, _('International'))
	)
	
	dob = forms.DateField(label=_('Date of birth'), widget=SelectDateWidget(), required=False)
	course = forms.CharField(label=_('Course'), max_length=128, required=False)
	uni_start = forms.DateField(label=_('Started university'), widget=SelectMonthYearWidget(), required=False)
	uni_end = forms.DateField(label=_('Will finish university'), widget=SelectMonthYearWidget(), required=False)
	university = forms.ModelChoiceField(queryset=University.objects.all(), required=False)
	course_type = forms.ChoiceField(label=_('Course level'), choices=COURSE_TYPE_CHOICES, required=False)
	student_type = forms.ChoiceField(label=_('Student type'), choices=STUDENT_TYPE_CHOICES, required=False)
	bio = forms.CharField(label=_('About me (for profile page)'), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	#job_title = forms.CharField(_('Job title'), max_length=128, required=False)
	#company = forms.CharField(_('Company'), max_length=128, required=False)

# User preferences
class FormPartFour(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(FormPartFour, self).__init__(*args, **kwargs)
		self.fields['email_chapter_optin'].label='Allow ' + chapter.name + ' to send me email updates'
		self.fields['mobile_marketing_optin'].label='Allow ' + chapter.name + ' to send me SMS updates'

	email_reminder_optin = forms.BooleanField(label=_('Allow email reminders about my upcoming school visits'), initial=True, required=False)
	mobile_reminder_optin = forms.BooleanField(label=_('Allow SMS reminders about my upcoming school visits'), initial=True, required=False)
	email_chapter_optin = forms.BooleanField(initial=True, required=False)
	mobile_marketing_optin = forms.BooleanField(initial=True, required=False)
	email_newsletter_optin = forms.BooleanField(label=_('Subscribe to The Amplifier, the monthly email newsletter of Robogals Global'), initial=True, required=False)

# Bio
class FormPartFive(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(FormPartFive, self).__init__(*args, **kwargs)

	trained = forms.BooleanField(label=_('Trained and approved to teach'), initial=False, required=False)
	internal_notes = forms.CharField(label=_('Internal notes'), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))

def edituser(request, username, chapter=None):
	pwerr = ''
	usererr = ''
	new_username = ''
	if username == '':
		join = True
		u = User()
		if request.user.is_superuser or (request.user.is_staff and request.user.chapter == chapter):
			adduser = True
		else:
			adduser = False
	else:
		join = False
		adduser = False
		if not request.user.is_authenticated():
			return HttpResponseRedirect("/login/?next=/profile/edit/")
		u = get_object_or_404(User, username__exact=username)
		chapter = u.chapter
	if join or request.user.is_superuser or request.user.id == u.id or (request.user.is_staff and request.user.chapter == u.chapter):
		if request.method == 'POST':
			if join:
				new_username = request.POST['username'].strip()
			formpart1 = FormPartOne(request.POST, chapter=chapter)
			formpart2 = FormPartTwo(request.POST, chapter=chapter)
			formpart3 = FormPartThree(request.POST, chapter=chapter)
			formpart4 = FormPartFour(request.POST, chapter=chapter)
			formpart5 = FormPartFive(request.POST, chapter=chapter)
			if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid() and formpart4.is_valid() and formpart5.is_valid():
				if join:
					username_len = len(new_username)
					if username_len < 3:
						usererr = _('Your username must be 3 or more characters')
					elif username_len > 30:
						usererr = _('Your username must be less than 30 characters')
					matches = re.compile(r'^\w+$').findall(new_username)
					if matches == []:
						usererr = _('Your username must contain only letters, numbers and underscores')
					else:
						try:
							usercheck = User.objects.get(username=new_username)
						except User.DoesNotExist:
							if request.POST['password1'] == request.POST['password2']:
								if len(request.POST['password1']) < 5:
									pwerr = _('Your password must be at least 5 characters long')
								else:
									u = User.objects.create_user(new_username, '', request.POST['password1'])
									u.chapter = chapter
									mt = MemberStatus(user_id=u.pk, statusType_id=1)
									mt.save()
									u.is_active = True
									u.is_staff = False
									u.is_superuser = False
									u.save()
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
					if 'student_number' in data:
						u.student_number = data['student_number']
					if 'union_member' in data:
						u.union_member = data['union_member']
					if 'tshirt' in data:
						u.tshirt = data['tshirt']
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
					u.course_type = data['course_type']
					u.student_type = data['student_type']
					u.bio = data['bio']
					#u.job_title = data['job_title']
					#u.company = data['company']
					data = formpart4.cleaned_data
					u.email_reminder_optin = data['email_reminder_optin']
					u.email_chapter_optin = data['email_chapter_optin']
					u.mobile_reminder_optin = data['mobile_reminder_optin']
					u.mobile_marketing_optin = data['mobile_marketing_optin']
					u.email_newsletter_optin = data['email_newsletter_optin']
					data = formpart5.cleaned_data
					if 'internal_notes' in data:
						u.internal_notes = data['internal_notes']
					if 'trained' in data:
						u.trained = data['trained']
					u.save()
					if 'return' in request.POST:
						request.user.message_set.create(message=unicode(_("Profile and settings updated!")))
						return HttpResponseRedirect(request.POST['return'])
					elif join:
						if chapter.welcome_email_enable:
							message = EmailMessage()
							message.subject = chapter.welcome_email_subject
							try:
								message.subject = chapter.welcome_email_subject.format(
									chapter=chapter,
									user=u,
									plaintext_password=request.POST['password1'])
							except Exception:
								message.subject = chapter.welcome_email_subject
							try:
								message.body = chapter.welcome_email_msg.format(
									chapter=chapter,
									user=u,
									plaintext_password=request.POST['password1'])
							except Exception:
								message.body = chapter.welcome_email_msg
							message.from_address = 'my@robogals.org'
							message.reply_address = 'my@robogals.org'
							message.from_name = chapter.name
							message.sender = User.objects.get(username='edit')
							message.html = chapter.welcome_email_html
							message.status = -1
							message.save()
							recipient = EmailRecipient()
							recipient.message = message
							recipient.user = u
							recipient.to_name = u.get_full_name()
							recipient.to_address = u.email
							recipient.save()
							message.status = 0
							message.save()
						return HttpResponseRedirect("/welcome/" + chapter.myrobogals_url + "/")
					else:
						request.user.message_set.create(message=unicode(_("Profile and settings updated!")))
						return HttpResponseRedirect("/profile/" + username + "/")
		else:
			if join:
				formpart1 = FormPartOne(None, chapter=chapter)
				formpart2 = FormPartTwo(None, chapter=chapter)
				formpart3 = FormPartThree(None, chapter=chapter)
				formpart4 = FormPartFour(None, chapter=chapter)
				formpart5 = FormPartFive(None, chapter=chapter)
			else:
				if u.tshirt:
					tshirt_id = u.tshirt.pk
				else:
					tshirt_id = None
				formpart1 = FormPartOne({
					'first_name': u.first_name,
					'last_name': u.last_name,
					'email': u.email,
					'alt_email': u.alt_email,
					'mobile': u.mobile,
					'gender': u.gender,
					'student_number': u.student_number,
					'union_member': u.union_member,
					'tshirt': tshirt_id}, chapter=chapter)
				formpart2 = FormPartTwo({
					'privacy': u.privacy,
					'dob_public': u.dob_public,
					'email_public': u.email_public}, chapter=chapter)
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
					'company': u.company,
					'course_type': u.course_type,
					'student_type': u.student_type,
					'bio': u.bio}, chapter=chapter)
				formpart4 = FormPartFour({
					'email_reminder_optin': u.email_reminder_optin,
					'email_chapter_optin': u.email_chapter_optin,
					'mobile_reminder_optin': u.mobile_reminder_optin,
					'mobile_marketing_optin': u.mobile_marketing_optin,
					'email_newsletter_optin': u.email_newsletter_optin}, chapter=chapter)
				formpart5 = FormPartFive({
					'internal_notes': u.internal_notes,
					'trained': u.trained}, chapter=chapter)
		if 'return' in request.GET:
			return_url = request.GET['return']
		elif 'return' in request.POST:
			return_url = request.POST['return']
		else:
			return_url = ''

		chpass = (join or (request.user.is_staff and request.user != u))
		exec_fields = request.user.is_superuser or (request.user.is_staff and request.user.chapter == chapter)
		return render_to_response('profile_edit.html', {'join': join, 'adduser': adduser, 'chpass': chpass, 'exec_fields': exec_fields, 'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3, 'formpart4': formpart4, 'formpart5': formpart5, 'u': u, 'chapter': chapter, 'usererr': usererr, 'pwerr': pwerr, 'new_username': new_username, 'return': return_url}, context_instance=RequestContext(request))
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
	try:
		next = request.POST['next']
	except KeyError:
		try:
			next = request.GET['next']
		except KeyError:
			next = '/'
	username = request.POST['username']
	password = request.POST['password']
	if email_re.match(username):
		try:
			users = User.objects.filter(email=username)
		except User.DoesNotExist:
			return render_to_response('login_form.html', {'username': username, 'error': 'Invalid email address or password', 'next': next}, context_instance=RequestContext(request))
		if len(users) > 1:
			return render_to_response('login_form.html', {'username': username, 'error': 'That email address has multiple users associated with it. Please log in using your username.', 'next': next}, context_instance=RequestContext(request))
		else:
			username = users[0].username
			emaillogin = True
	else:
		emaillogin = False
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			return HttpResponseRedirect(next)
		else:
			return render_to_response('login_form.html', {'username': username, 'error': 'Your account has been disabled', 'next': next}, context_instance=RequestContext(request))
	else:
		if emaillogin:
			return render_to_response('login_form.html', {'username': username, 'error': 'Invalid email address or password', 'next': next}, context_instance=RequestContext(request))
		else:
			return render_to_response('login_form.html', {'username': username, 'error': 'Invalid username or password', 'next': next}, context_instance=RequestContext(request))

class CSVUploadForm(forms.Form):
	csvfile = forms.FileField()

class WelcomeEmailForm(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(WelcomeEmailForm, self).__init__(*args, **kwargs)
		self.fields['subject'].initial = chapter.welcome_email_subject
		self.fields['body'].initial = chapter.welcome_email_msg
		self.fields['html'].initial = chapter.welcome_email_html

	importaction = forms.ChoiceField(choices=((1,_('Add members, and send welcome email')),(2,_('Add members, with no further action'))),initial=1)
	subject = forms.CharField(max_length=256, required=False)
	body = forms.CharField(widget=forms.Textarea, required=False)
	html = forms.BooleanField(required=False)

class DefaultsFormOne(forms.Form):
	GENDERS = (
		(0, '---'),
		(1, 'Male'),
		(2, 'Female'),
	)

	COURSE_TYPE_CHOICES = (
		(0, '---'),
		(1, 'Undergraduate'),
		(2, 'Postgraduate')
	)
	
	STUDENT_TYPE_CHOICES = (
		(0, '---'),
		(1, 'Local'),
		(2, 'International')
	)

	date_joined = forms.DateField(label=_('Date joined'), widget=SelectDateWidget(), required=False)
	gender = forms.ChoiceField(choices=GENDERS, initial=0)
	uni_start = forms.DateField(label=_('Started university'), widget=SelectMonthYearWidget(), required=False)
	uni_end = forms.DateField(label=_('Will finish university'), widget=SelectMonthYearWidget(), required=False)
	university = forms.ModelChoiceField(queryset=University.objects.all(), required=False)
	course_type = forms.ChoiceField(label=_('Course level'), choices=COURSE_TYPE_CHOICES, required=False)
	student_type = forms.ChoiceField(label=_('Student type'), choices=STUDENT_TYPE_CHOICES, required=False)

class DefaultsFormTwo(forms.Form):
	email_reminder_optin = forms.BooleanField(label=_('Allow email reminders about upcoming school visits'), initial=True, required=False)
	mobile_reminder_optin = forms.BooleanField(label=_('Allow SMS reminders about upcoming school visits'), initial=True, required=False)
	email_chapter_optin = forms.BooleanField(label=_('Allow email updates from local Robogals chapter'), initial=True, required=False)
	mobile_marketing_optin = forms.BooleanField(label=_('Allow SMS updates from local Robogals chapter'), initial=True, required=False)
	email_newsletter_optin = forms.BooleanField(label=_('Subscribe to The Amplifier, the monthly email newsletter of Robogals Global'), initial=True, required=False)

@login_required
def importusers(request, chapterurl):
	chapter = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if not (request.user.is_superuser or (request.user.is_staff and (chapter == request.user.chapter))):
		raise Http404
	errmsg = None
	if request.method == 'POST':
		if request.POST['step'] == '1':
			form = CSVUploadForm(request.POST, request.FILES)
			welcomeform = WelcomeEmailForm(request.POST, chapter=chapter)
			defaultsform1 = DefaultsFormOne(request.POST)
			defaultsform2 = DefaultsFormTwo(request.POST)
			if form.is_valid() and welcomeform.is_valid() and defaultsform1.is_valid() and defaultsform2.is_valid():
				file = request.FILES['csvfile']
				tmppath = "/tmp/" + request.user.chapter.myrobogals_url + request.user.username + str(time()) + ".csv"
				destination = open(tmppath, 'w')
				for chunk in file.chunks():
					destination.write(chunk)
				destination.close()
				fp = open(tmppath, 'rU')
				filerows = csv.reader(fp)
				defaults = {}
				defaults.update(defaultsform1.cleaned_data)
				defaults.update(defaultsform2.cleaned_data)
				welcomeemail = welcomeform.cleaned_data
				request.session['welcomeemail'] = welcomeemail
				request.session['defaults'] = defaults
				return render_to_response('import_users_2.html', {'tmppath': tmppath, 'filerows': filerows, 'chapter': chapter}, context_instance=RequestContext(request))
		elif request.POST['step'] == '2':
			if 'tmppath' not in request.POST:
				return HttpResponseRedirect("/chapters/" + chapterurl + "/edit/users/import/")
			tmppath = request.POST['tmppath']
			fp = open(tmppath, 'rU')
			filerows = csv.reader(fp)
			welcomeemail = request.session['welcomeemail']
			if welcomeemail['importaction'] == '2':
				welcomeemail = None
			defaults = request.session['defaults']
			try:
				users_imported = importcsv(filerows, welcomeemail, defaults, chapter)
			except RgImportCsvException as e:
				errmsg = e.errmsg
				return render_to_response('import_users_2.html', {'tmppath': tmppath, 'filerows': filerows, 'chapter': chapter, 'errmsg': errmsg}, context_instance=RequestContext(request))
			if welcomeemail == None:
				msg = _('%d users imported!') % users_imported
			else:
				msg = _('%d users imported and emailed!') % users_imported
			request.user.message_set.create(message=unicode(msg))
			del request.session['welcomeemail']
			del request.session['defaults']
			return HttpResponseRedirect('/chapters/' + chapter.myrobogals_url + '/edit/users/')
	else:
		form = CSVUploadForm()
		welcomeform = WelcomeEmailForm(None, chapter=chapter)
		defaultsform1 = DefaultsFormOne()
		defaultsform2 = DefaultsFormTwo()
	return render_to_response('import_users_1.html', {'chapter': chapter, 'form': form, 'welcomeform': welcomeform, 'defaultsform1': defaultsform1, 'defaultsform2': defaultsform2, 'errmsg': errmsg}, context_instance=RequestContext(request))

COMPULSORY_FIELDS = (
	('first_name', 'First name'),
	('last_name', 'Last name'),
	('email', 'Primary email address'),
)

CREDENTIALS_FIELDS = (
	('username', 'myRobogals username. If blank, a username will be generated based upon their first name, last name or email address, as necessary to generate a username that is unique in the system. The new username will be included in their welcome email.'),
	('password', 'myRobogals password. If blank, a new password will be generated for them and included in their welcome email.'),
)

BASIC_FIELDS = (
	('alt_email', 'Alternate email address'),
	('mobile', 'Mobile number, in correct local format, OR correct local format with the leading 0 missing (as Excel is prone to do), OR international format without a leading +. Examples: 61429558100 (Aus) or 447553333111 (UK)'),
	('date_joined', 'Date when this member joined Robogals. If blank, today\'s date is used'),
	('dob', 'Date of birth, in format 1988-10-26'),
	('gender', '0 = No answer; 1 = Male; 2 = Female'),
)

EXTRA_FIELDS = (
	('course', 'Name of course/degree'),
	('uni_start', 'Date when they commenced university, in format 2007-02-28'),
	('uni_end', 'Date when they expect to complete university, in format 2011-11-30'),
	('university_id', 'University they attend. Enter -1 to use the host university of this Robogals chapter. For a full list of IDs see https://my.robogals.org/chapters/<chapter>/edit/users/import/help/unis/'),
	('course_type', '1 = Undergraduate; 2 = Postgraduate'),
	('student_type', '1 = Domestic student; 2 = International student'),
	('student_number', 'Student number, a.k.a. enrolment number, candidate number, etc.'),
)

PRIVACY_FIELDS = (
	('privacy', '20 = Profile viewable to public internet; 10 = Profile viewable only to Robogals members; 5 = Profile viewable only to Robogals members from same chapter; 0 = Profile viewable only to exec'),
	('dob_public', 'Either \'True\' or \'False\', specifies whether their date of birth should be displayed in their profile page'),
	('email_public', 'Either \'True\' or \'False\', specifies whether their email address should be displayed in their profile page'),
	('email_chapter_optin', 'Either \'True\' or \'False\', specifies whether this member will receive general emails sent by this Robogals chapter'),
	('mobile_marketing_optin', 'Either \'True\' or \'False\', specifies whether this member will receive general SMSes sent by this Robogals chapter'),
	('email_reminder_optin', 'Either \'True\' or \'False\', specifies whether this member will receive email reminders about school visits from myRobogals'),
	('mobile_reminder_optin', 'Either \'True\' or \'False\', specifies whether this member will receive SMS reminders about school visits from myRobogals'),
	('email_newsletter_optin', 'Either \'True\' or \'False\', specifies whether this member will receive The Amplifier, the monthly email newsletter of Robogals Global'),
)

HELPINFO = (
	("Compulsory fields", COMPULSORY_FIELDS),
	("Credentials fields", CREDENTIALS_FIELDS),
	("Basic fields", BASIC_FIELDS),
	("Extra fields", EXTRA_FIELDS),
	("Privacy fields", PRIVACY_FIELDS)
)

@login_required
def importusershelp(request, chapterurl):
	chapter = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if not (request.user.is_superuser or (request.user.is_staff and (chapter == request.user.chapter))):
		raise Http404
	return render_to_response('import_users_help.html', {'HELPINFO': HELPINFO}, context_instance=RequestContext(request))

class WelcomeEmailFormTwo(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(WelcomeEmailFormTwo, self).__init__(*args, **kwargs)
		self.fields['subject'].initial = chapter.welcome_email_subject
		self.fields['body'].initial = chapter.welcome_email_msg
		self.fields['html'].initial = chapter.welcome_email_html

	subject = forms.CharField(max_length=256)
	body = forms.CharField(widget=forms.Textarea)
	html = forms.BooleanField(required=False)

@login_required
def genpw(request, username):
	user = get_object_or_404(User, username__exact=username)
	chapter = user.chapter
	if not (request.user.is_superuser or (request.user.is_staff and (chapter == request.user.chapter))):
		raise Http404
	if 'return' in request.GET:
		return_url = request.GET['return']
	elif 'return' in request.POST:
		return_url = request.POST['return']
	else:
		return_url = ''
	errmsg = ''
	if request.method == 'POST':
		welcomeform = WelcomeEmailFormTwo(request.POST, chapter=chapter)
		if welcomeform.is_valid():
			welcomeemail = welcomeform.cleaned_data
			try:
				genandsendpw(user, welcomeemail, chapter)
				request.user.message_set.create(message=unicode(_("Password generated and emailed")))
				if return_url == '':
					return_url = '/profile/' + username + '/edit/'
				return HttpResponseRedirect(return_url)
			except RgGenAndSendPwException as e:
				errmsg = e.errmsg
	else:
		welcomeform = WelcomeEmailFormTwo(None, chapter=chapter)
	return render_to_response('genpw.html', {'welcomeform': welcomeform, 'username': user.username, 'chapter': chapter, 'return': return_url, 'error': errmsg}, context_instance=RequestContext(request))

@login_required
def unilist(request, chapterurl):
	chapter = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if not (request.user.is_superuser or (request.user.is_staff and (chapter == request.user.chapter))):
		raise Http404
	unis = University.objects.all()
	return render_to_response('uni_ids_list.html', {'unis': unis}, context_instance=RequestContext(request))
