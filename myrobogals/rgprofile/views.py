import csv
import operator
import re
from datetime import datetime, time, date
from time import time

from django import forms
from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.widgets import Widget, Select, TextInput
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from myrobogals.rgchapter.models import Chapter
from myrobogals.rgchapter.models import DisplayColumn, ShirtSize
from myrobogals.rgmain.models import University, MobileRegex
from myrobogals.rgmain.utils import SelectDateWidget, email_re
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient, SMSMessage, SMSRecipient
from myrobogals.rgprofile.functions import importcsv, genandsendpw, any_exec_attr, RgImportCsvException, \
	RgGenAndSendPwException
from myrobogals.rgprofile.models import Position, UserList
from myrobogals.rgprofile.models import User, MemberStatus, MemberStatusType
from myrobogals.rgteaching.models import EventAttendee, Event
from myrobogals.settings import MEDIA_URL, GENDERS


def joinchapter(request, chapterurl):
	chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
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
	c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
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

class EditStatusForm(forms.Form):
	status = forms.CharField()
	users = EmailModelMultipleChoiceField(queryset=User.objects.none(), widget=FilteredSelectMultiple(_("Members"), False, attrs={'rows': 20}), required=True)

	def __init__(self, *args, **kwargs):
		user=kwargs['user']
		del kwargs['user']
		super(EditStatusForm, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['users'].queryset = User.objects.filter(is_active=True).order_by('last_name')
		else:
			self.fields['users'].queryset = User.objects.filter(chapter=user.chapter, is_active=True).order_by('last_name')

@login_required
def listuserlists(request, chapterurl):
	c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
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
	c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
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
				messages.success(request, message=unicode(_("User list \"%(listname)s\" has been updated") % {'listname': l.name}))
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
	c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
	memberstatustypes = MemberStatusType.objects.all()
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		search = ''
		searchsql = ''
		if 'search' in request.GET:
			search = request.GET['search']
			search_fields = ['username', 'first_name', 'last_name', 'email', 'mobile']
			for field in search_fields:
				searchsql = searchsql + ' OR ' + field + ' LIKE "%%' + search + '%%" '
			searchsql = 'AND (' + searchsql[4:] + ')'
		if 'status' in request.GET:
			status = request.GET['status']
		else:
			status = '1'   # Default to student members

		if (status != '0'):
			users = User.objects.raw('SELECT u.* FROM rgprofile_user AS u, rgprofile_memberstatus AS ms WHERE u.chapter_id ' +
					'= '+ str(c.pk) +' AND u.id = ms.user_id AND ms.statusType_id = '+ status +' AND ms.status_date_end IS NULL ' +
					searchsql + ' ORDER BY last_name, first_name')
		else:
			users = User.objects.raw('SELECT u.* FROM rgprofile_user AS u WHERE u.chapter_id ' +
					'= '+ str(c.pk) + ' ' +
					searchsql + ' ORDER BY last_name, first_name')
		display_columns = c.display_columns.all()
		return render_to_response('user_list.html', {'memberstatustypes': memberstatustypes, 'users': users, 'numusers': len(list(users)), 'search': search, 'status': int(status), 'chapter': c, 'display_columns': display_columns, 'return': request.path + '?' + request.META['QUERY_STRING'], 'MEDIA_URL': MEDIA_URL}, context_instance=RequestContext(request))
	else:
		raise Http404

@login_required
def deleteuser(request, userpk):
	userToBeDeleted = get_object_or_404(User, pk=userpk)
	if request.user.is_superuser or (request.user.is_staff and (userToBeDeleted.chapter == request.user.chapter)):
		msg = ''
		old_status = userToBeDeleted.memberstatus_set.get(status_date_end__isnull=True)
		canNotDelete = False
		if Position.objects.filter(user=userToBeDeleted):
			msg = _('<br>Member "%s" has held at least one officeholder position. ') % userToBeDeleted.get_full_name()
			canNotDelete = True
		if EventAttendee.objects.filter(user=userToBeDeleted, actual_status=1):
			msg += _('<br>Member "%s" has attended at least one school visit. ') % userToBeDeleted.get_full_name()
			canNotDelete = True
		if Event.objects.filter(creator=userToBeDeleted):
			msg += _('<br>Member "%s" has created at least one school visit. ') % userToBeDeleted.get_full_name()
			canNotDelete = True
		if EmailMessage.objects.filter(sender=userToBeDeleted):
			msg += _('<br>Member "%s" has sent at least one email. ') % userToBeDeleted.get_full_name()
			canNotDelete = True
		if SMSMessage.objects.filter(sender=userToBeDeleted):
			msg += _('<br>Member "%s" has sent at least one SMS message. ') % userToBeDeleted.get_full_name()
			canNotDelete = True
		if LogEntry.objects.filter(user=userToBeDeleted):
			msg += _('<br>Member "%s" owned at least one admin log object. ') % userToBeDeleted.get_full_name()
			canNotDelete = True
		if not canNotDelete:
			if (request.method != 'POST') or (('delete' not in request.POST) and ('alumni' not in request.POST)):
				return render_to_response('user_delete_confirm.html', {'userToBeDeleted': userToBeDeleted, 'return': request.GET['return']}, context_instance=RequestContext(request))
			else:
				if ('delete' in request.POST) and ('alumni' not in request.POST):
					userToBeDeleted.delete()
					msg = _('Member "%s" deleted') % userToBeDeleted.get_full_name()
				elif ('delete' not in request.POST) and ('alumni' in request.POST):
					if old_status.statusType == MemberStatusType.objects.get(pk=2):
						msg = _('Member "%s" is already marked as alumni') % userToBeDeleted.get_full_name()
					else:
						if userToBeDeleted.membertype().description != 'Inactive':
							old_status.status_date_end = date.today()
							old_status.save()
						new_status=MemberStatus()
						new_status.user = userToBeDeleted
						new_status.statusType = MemberStatusType.objects.get(pk=2)
						new_status.status_date_start = date.today()
						new_status.save()
						msg = _('Member "%s" marked as alumni') % userToBeDeleted.get_full_name()
				else:
					raise Http404
		if canNotDelete:
			messages.success(request, message=unicode(_('- Cannot delete member. Reason(s): %s<br>Consider marking this member as alumni instead.') % msg))
		else:
			messages.success(request, message=unicode(msg))
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		else:
			return HttpResponseRedirect('/chapters/' + request.user.chapter.myrobogals_url + '/edit/users/?search=&status=' + str(old_status.statusType.pk))
	else:
		raise Http404

@login_required
def editexecs(request, chapterurl):
	c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		users = User.objects.filter(chapter=c)
		search = ''
		if 'search' in request.GET:
			search = request.GET['search']
			users = users.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(mobile__icontains=search))
		users = users.order_by('last_name', 'first_name')
		exec_users = filter(any_exec_attr, users)
		return render_to_response('exec_list.html', {'users': exec_users, 'search': search, 'chapter': c, 'return': request.path + '?' + request.META['QUERY_STRING']}, context_instance=RequestContext(request))
	else:
		raise Http404

@login_required
def editstatus(request, chapterurl):
	c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
	memberstatustypes = MemberStatusType.objects.all()
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		users = []
		if request.method == 'POST':
			ulform = EditStatusForm(request.POST, user=request.user)
			if ulform.is_valid():
				data = ulform.cleaned_data
				status = data['status']
				users = data['users'] #l:queryset
				users_already = ""
				users_changed = ""

				for user in users:
					u = User.objects.get(username__exact = user.username)
					old_status = u.memberstatus_set.get(status_date_end__isnull=True)
					if old_status.statusType == MemberStatusType.objects.get(pk=int(status)):
						if(users_already):
							users_already = users_already + ", " + u.username
						else:
							users_already = u.username
					else:
						if user.membertype().description != 'Inactive':
							old_status.status_date_end = date.today()
							old_status.save()
						new_status=MemberStatus()
						new_status.user = u
						new_status.statusType = MemberStatusType.objects.get(pk=int(status))
						new_status.status_date_start = date.today()
						new_status.save()
						if(users_changed):
							users_changed = users_changed + ", " + u.username
						else:
							users_changed = u.username

				if(users_already):
					messages.success(request, message=unicode(_("%(usernames)s are already marked as %(type)s") % {'usernames': users_already, 'type': MemberStatusType.objects.get(pk=int(status)).description}))

				if(users_changed):
					messages.success(request, message=unicode(_("%(usernames)s has/have been marked as %(type)s") % {'usernames': users_changed, 'type': new_status.statusType.description}))

				return HttpResponseRedirect('/chapters/' + chapterurl + '/edit/users/')
			else:
				return render_to_response('edit_user_status.html', {'ulform': ulform, 'chapter': c, 'memberstatustypes': memberstatustypes}, context_instance=RequestContext(request))
		else:
			ulform = EditStatusForm(None, user=request.user)
			return render_to_response('edit_user_status.html', {'ulform': ulform, 'chapter': c, 'memberstatustypes': memberstatustypes}, context_instance=RequestContext(request))

@login_required
def adduser(request, chapterurl):
	chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
	return edituser(request, '', chapter)

@login_required
def redirtoself(request):
	return HttpResponseRedirect("/profile/" + request.user.username + "/")

@login_required
def mobverify(request):
	if not request.user.is_staff:
		raise Http404
	if request.user.mobile_verified:
		messages.success(request, message=unicode(_('Your mobile number is already verified')))
		return HttpResponseRedirect('/profile/')
	if request.method == 'POST':
		if not request.session.get('verif_code', False):
			raise Http404
		if not request.session.get('mobile', False):
			del request.session['verif_code']
			raise Http404
		if (request.POST['verif_code'] == request.session['verif_code']) and (request.user.mobile == request.session['mobile']):
			request.user.mobile_verified = True
			request.user.save()
			msg = _('Verification succeeded')
		else:
			msg = _('- Verification failed: invalid verification code')
		del request.session['verif_code']
		del request.session['mobile']
		messages.success(request, message=unicode(msg))
		return HttpResponseRedirect('/messages/sms/write/')
	else:
		if request.user.mobile:
			verif_code = User.objects.make_random_password(6)
			message = SMSMessage()
			message.body = 'Robogals verification code: ' + verif_code
			message.senderid = '61429558100'
			message.sender = User.objects.get(username='edit')
			message.chapter = Chapter.objects.get(pk=1)
			message.validate()
			message.sms_type = 1
			message.status = -1
			message.save()
			recipient = SMSRecipient()
			recipient.message = message
			recipient.user = request.user
			request.session['mobile'] = request.user.mobile
			recipient.to_number = request.session['mobile']
			recipient.save()

			# Check that we haven't used too many credits
			sms_this_month = 0
			sms_this_month_obj = SMSMessage.objects.filter(date__gte=datetime(now().year, now().month, 1, 0, 0, 0), status__in=[0, 1])
			for obj in sms_this_month_obj:
				sms_this_month += obj.credits_used()
			sms_this_month += message.credits_used()
			if sms_this_month > Chapter.objects.get(pk=1).sms_limit:
				message.status = 3
				message.save()
				msg = _('- Verification failed: system problem please try again later')
				messages.success(request, message=unicode(msg))
				return HttpResponseRedirect('/profile/')

			message.status = 0
			message.save()
			request.session['verif_code'] = verif_code
			return render_to_response('profile_mobverify.html', {}, context_instance=RequestContext(request))
		else:
			msg = _('- Verification failed: no mobile number entered. (Profile -> Edit Profile)')
			messages.success(request, message=unicode(msg))
			return HttpResponseRedirect('/messages/sms/write/')

@login_required
def redirtoeditself(request):
	return HttpResponseRedirect("/profile/" + request.user.username + "/edit/")

# Shows the profile of your user
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
	account_list = list(set(account for account in u.aliases.all()).union(set(account for account in u.user_aliases.all())).union(set([u])))
	for account in account_list:
		subAliasesSet = set(ac for ac in account.aliases.all())
		supAliasesSet = set(ac for ac in account.user_aliases.all())
		subset = subAliasesSet.union(supAliasesSet)
		for alias in subset:
			if alias not in account_list:
				account_list.append(alias)
	visits = EventAttendee.objects.filter(user__in=account_list, actual_status=1).order_by('-event__visit_start')
	return render_to_response('profile_view.html', {'user': u, 'current_positions': current_positions, 'past_positions': past_positions, 'visits': visits}, context_instance=RequestContext(request))

@login_required
def contactdirectory(request):
	if not request.user.is_staff:
		raise Http404
	results = []
	name = ''
	if ('name' in request.GET) and (request.GET['name'] != ''):
		name = request.GET['name']
		for u in User.objects.filter(reduce(operator.or_, ((Q(first_name__icontains=x) | Q(last_name__icontains=x)) for x in name.split()))):
			if u.has_cur_pos():
				results.append(u)
	return render_to_response('contact_directory.html', {'results': results, 'name': name}, context_instance=RequestContext(request))

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
			this_year = date.today().year
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

# Custom student number field
class StudentNumField(forms.CharField):
	def __init__(self, *args, **kwargs):
		self.chapter=None
		self.user_id=None
		super(StudentNumField, self).__init__(*args, **kwargs)

	# This function checks for the uniqueness of the student number within the chapter.
	# Student numbers may not necessarily be unique globally across all universities,
	# thus one cannot simply use the built-in Django functionality to specify this field
	# as a unique field.
	def clean(self, value):
		if value == '':
			if self.required:
				raise forms.ValidationError(_('This field is required.'))
			else:
				return ''
		if User.objects.filter(Q(chapter=self.chapter), ~Q(pk=self.user_id), Q(student_number=value)).count() > 0:
			raise forms.ValidationError(_('There is already a member with that student number. Click "forgot password" to the left to recover your existing account, if necessary.'))
		else:
			return value

# Custom t-shirt size selection field
class ShirtChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.size_long

# Personal information
class FormPartOne(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		user_id=kwargs['user_id']
		del kwargs['user_id']
		super(FormPartOne, self).__init__(*args, **kwargs)
		self.fields['mobile'] = MobileField(label=_('Mobile phone'), max_length=20, required=False, widget=MobileTextInput(), chapter=chapter)

		if chapter.student_number_enable:
			self.fields['student_number'].label = chapter.student_number_label
			self.fields['student_number'].required = chapter.student_number_required
			self.fields['student_number'].chapter = chapter
			self.fields['student_number'].user_id = user_id
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

		if chapter.police_check_number_enable:
			self.fields['police_check_number'].label = chapter.police_check_number_label
			self.fields['police_check_expiration'].label = 'Expiration Date'
			self.fields['police_check_number'].required = chapter.police_check_number_required
			self.fields['police_check_expiration'].required = chapter.police_check_number_required
		else:
			del self.fields['police_check_number']
			del self.fields['police_check_expiration']

	first_name = forms.CharField(label=_('First name'), max_length=30)
	last_name = forms.CharField(label=_('Last name'), max_length=30)
	username = forms.CharField(label=_('Username'), max_length=30)
	email = forms.EmailField(label=_('Email'), max_length=64)
	student_number = StudentNumField(max_length=32)
	union_member = forms.BooleanField()
	tshirt = ShirtChoiceField(queryset=ShirtSize.objects.none())
	alt_email = forms.EmailField(label=_('Alternate email'), max_length=64, required=False)
	mobile = forms.BooleanField()
	gender = forms.ChoiceField(label=_('Gender'), choices=GENDERS)
	police_check_number = forms.CharField(help_text=_("Also known as the number that allows you to volunteer with Robogals. Ask an executive member if unsure. When this number is entered, your chapter's executive members will be notified"))
	police_check_expiration = forms.DateField(widget=SelectDateWidget(), help_text=_("You must also enter an expiration date shown on your card. myRobogals will inform you and your chapter executives when the card is about to expire"))

	def clean(self):
		cleaned_data = super(FormPartOne, self).clean()
		police_check_number = cleaned_data.get("police_check_number")
		police_check_expiration = cleaned_data.get("police_check_expiration")

		if police_check_number and police_check_expiration:
			# Only check expiration date if field is required and the user has entered a p/c number
			if self.fields['police_check_expiration'].required or police_check_number != '':
				local_time = datetime.date(now())

				# Check if card has expired in their local time only if they've made changes
				if police_check_expiration < local_time:
					self.add_error('police_check_expiration', 'The card you have entered has already expired')
			else:
				cleaned_data["police_check_expiration"] = None

		return cleaned_data

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

# Profile information
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
	university = forms.ModelChoiceField(label=_('University'), queryset=University.objects.all(), required=False)
	course_type = forms.ChoiceField(label=_('Course level'), choices=COURSE_TYPE_CHOICES, required=False)
	student_type = forms.ChoiceField(label=_('Student type'), choices=STUDENT_TYPE_CHOICES, required=False)
	job_title = forms.CharField(label=_('Occupation'), max_length=128, required=False)
	company = forms.CharField(label=_('Employer'), max_length=128, required=False)
	bio = forms.CharField(label=_('About me (for profile page)'), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	#job_title = forms.CharField(_('Job title'), max_length=128, required=False)
	#company = forms.CharField(_('Company'), max_length=128, required=False)

# User preferences
class FormPartFour(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(FormPartFour, self).__init__(*args, **kwargs)
		self.fields['email_chapter_optin'].label=_('Allow %s to send me email updates') % chapter.name
		self.fields['mobile_marketing_optin'].label=_('Allow %s to send me SMS updates') % chapter.name
		if chapter.country.code == 'AU':
			self.fields['email_careers_newsletter_AU_optin'].initial = True
		else:
			self.fields['email_careers_newsletter_AU_optin'].initial = False

	email_reminder_optin = forms.BooleanField(label=_('Allow email reminders about my upcoming school visits'), initial=True, required=False)
	mobile_reminder_optin = forms.BooleanField(label=_('Allow SMS reminders about my upcoming school visits'), initial=True, required=False)
	email_chapter_optin = forms.BooleanField(initial=True, required=False)
	mobile_marketing_optin = forms.BooleanField(initial=True, required=False)
	email_newsletter_optin = forms.BooleanField(label=_('Subscribe to The Amplifier, the monthly email newsletter of Robogals Global'), initial=True, required=False)
	email_careers_newsletter_AU_optin = forms.BooleanField(label=_('Subscribe to Robogals Careers Newsletter - Australia'), required=False)

# Bio
class FormPartFive(forms.Form):
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(FormPartFive, self).__init__(*args, **kwargs)

	security_check = forms.BooleanField(label=_('Passed the Police Check'), initial=False, required=False)
	trained = forms.BooleanField(label=_('Trained and approved to teach'), initial=False, required=False)
	internal_notes = forms.CharField(label=_('Internal notes'), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))

# Sends an email to everyone on the chapter notify list including saving message to database
def email_message(email_subject, email_body, chapter):
	message = EmailMessage()
	message.subject = email_subject
	message.body = email_body
	message.from_name = "myRobogals"
	message.from_address = "my@robogals.org"
	message.reply_address = "my@robogals.org"
	message.sender = User.objects.get(username='edit')
	message.html = True
	message.email_type = 0

	# Message is set to WAIT mode
	message.status = -1
	message.save()

	# Creates a list of all users to notify
	if chapter.notify_list != None:
		users_to_notify = chapter.notify_list.users.all()

		# Email to all users that need to be notified
		for user in users_to_notify:
			recipient = EmailRecipient()
			recipient.message = message
			recipient.user = user
			recipient.to_name = user.get_full_name()
			recipient.to_address = user.email
			recipient.save()
			message.status = 0
			message.save()

# Performs editing an existing as well as adding new user to a chapter
def edituser(request, username, chapter=None):
	pwerr = ''
	usererr = ''
	carderr = ''
	new_username = ''
	valid_card = False

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

		# Get reference to user
		u = get_object_or_404(User, username__exact=username)

		# Get user's chapter
		chapter = u.chapter

	# Either a superuser, self user or exec of chapter
	if join or request.user.is_superuser or request.user.id == u.id or (request.user.is_staff and request.user.chapter == u.chapter):
		# Form submission POST request
		if request.method == 'POST':
			# Obtaining the data from the post request
			formpart1 = FormPartOne(request.POST, chapter=chapter, user_id=u.id)
			formpart2 = FormPartTwo(request.POST, chapter=chapter)
			formpart3 = FormPartThree(request.POST, chapter=chapter)
			formpart4 = FormPartFour(request.POST, chapter=chapter)
			formpart5 = FormPartFive(request.POST, chapter=chapter)

			# Checking if the form is valid
			if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid() and formpart4.is_valid() and formpart5.is_valid():
				if ('internal_notes' in request.POST) or ('trained' in request.POST) or ('security_check' in request.POST):
					attempt_modify_exec_fields = True
				else:
					attempt_modify_exec_fields = False

				# Clean data from form1
				data = formpart1.cleaned_data

				# Issue new username if a new user or old user changes his username
				if join or (data['username'] != '' and data['username'] != u.username):
					new_username = data['username']

				# If new username, verify the length of the username
				if new_username:
					username_len = len(new_username)
					if username_len < 3:
						usererr = _('Your username must be 3 or more characters')
					elif username_len > 30:
						usererr = _('Your username must be less than 30 characters')

					# Regex check for words, letters, numbers and underscores only in username
					matches = re.compile(r'^\w+$').findall(new_username)
					if matches == []:
						usererr = _('Your username must contain only letters, numbers and underscores')

					# See if it already exists in database
					else:
						try:
							usercheck = User.objects.get(username=new_username)
						except User.DoesNotExist:
							if join:
								if request.POST['password1'] == request.POST['password2']:
									if len(request.POST['password1']) < 5:
										pwerr = _('Your password must be at least 5 characters long')
									else:
										# Creates, saves and returns a User object
										u = User.objects.create_user(new_username, '', request.POST['password1'])
										u.chapter = chapter
										mt = MemberStatus(user_id=u.pk, statusType_id=1)
										mt.save()
										u.is_active = True
										u.is_staff = False
										u.is_superuser = False

										if 'police_check_number' in data and 'police_check_expiration' in data:
											u.police_check_number = data['police_check_number']
											u.police_check_expiration = data['police_check_expiration']
											notify_chapter(chapter, u)

										u.save()
								else:
									pwerr = _('The password and repeated password did not match. Please try again')
						else:
							usererr = _('That username is already taken')

				# Chapter executive accessing the profile and trying to change a password
				if request.user.is_staff and request.user != u:
					if len(request.POST['password1']) > 0:
						if request.POST['password1'] == request.POST['password2']:
							# Sets the password if it's the same, doesn't save the user object
							u.set_password(request.POST['password1'])
						else:
							pwerr = _('The password and repeated password did not match. Please try again')

				# No password or username errors were encountered
				if pwerr == '' and usererr == '':
					# Form 1 data
					data = formpart1.cleaned_data
					u.first_name = data['first_name']
					u.last_name = data['last_name']

					if new_username:
						u.username = new_username

					username = data['username']
					u.email = data['email']
					u.alt_email = data['alt_email']

					if u.mobile != data['mobile']:
						u.mobile = data['mobile']
						u.mobile_verified = False

					u.gender = data['gender']

					if 'student_number' in data:
						u.student_number = data['student_number']
					if 'union_member' in data:
						u.union_member = data['union_member']
					if 'tshirt' in data:
						u.tshirt = data['tshirt']
					if 'police_check_number' in data and 'police_check_expiration' in data:
						# Send email only if the user has changed/added a police check number instead of removing
						if data['police_check_number'] != u.police_check_number and data['police_check_expiration'] != u.police_check_expiration:
							u.police_check_number = data['police_check_number']
							u.police_check_expiration = data['police_check_expiration']

							# Notify chapter of police number changes
							notify_chapter(chapter, u)

					# Form 2 data
					data = formpart2.cleaned_data
					u.privacy = data['privacy']
					u.dob_public = data['dob_public']
					u.email_public = data['email_public']

					# Form 3 data
					data = formpart3.cleaned_data
					u.dob = data['dob']
					u.course = data['course']
					u.uni_start = data['uni_start']
					u.uni_end = data['uni_end']
					u.university = data['university']
					u.course_type = data['course_type']
					u.student_type = data['student_type']
					u.job_title = data['job_title']
					u.company = data['company']
					u.bio = data['bio']
					#u.job_title = data['job_title']
					#u.company = data['company']

					# Form 4 data
					data = formpart4.cleaned_data
					u.email_reminder_optin = data['email_reminder_optin']
					u.email_chapter_optin = data['email_chapter_optin']
					u.mobile_reminder_optin = data['mobile_reminder_optin']
					u.mobile_marketing_optin = data['mobile_marketing_optin']
					u.email_newsletter_optin = data['email_newsletter_optin']
					u.email_careers_newsletter_AU_optin = data['email_careers_newsletter_AU_optin']

					# Check whether they have permissions to edit exec only fields
					if attempt_modify_exec_fields and (request.user.is_superuser or request.user.is_staff):
						data = formpart5.cleaned_data
						u.internal_notes = data['internal_notes']
						u.trained = data['trained']
						u.security_check = data['security_check']

					# Save user to database
					u.save()

					if 'return' in request.POST:
						# Renders successful message on page
						messages.success(request, message=unicode(_("%(username)s has been added to the chapter") % {'username': u.username}))

						# Returns rendered page
						return HttpResponseRedirect(request.POST['return'])

					# If it's a new user signup
					elif join:
						if chapter.welcome_email_enable:
							# Creates a new EmailMessage object preparing for an email
							message = EmailMessage()


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

							# Setting defaults
							message.from_address = 'my@robogals.org'
							message.reply_address = 'my@robogals.org'
							message.from_name = chapter.name
							message.sender = User.objects.get(username='edit')
							message.html = chapter.welcome_email_html

							# Setting message to -1 in the DB shows that the message is in WAIT mode
							message.status = -1
							message.save()

							# Prepares message for sending
							recipient = EmailRecipient()
							recipient.message = message
							recipient.user = u
							recipient.to_name = u.get_full_name()
							recipient.to_address = u.email
							recipient.save()

							# Change message to PENIDNG mode, which waits for server to send
							message.status = 0
							message.save()

						# Notifies chapter of a new member the user joined on their own
						if not adduser and chapter.notify_enable and chapter.notify_list:
							# Sends an email to every exec on the notify list
							message_subject = 'New user ' + u.get_full_name() + ' joined ' + chapter.name
							message_body = 'New user ' + u.get_full_name() + ' joined ' + chapter.name + '<br/>username: ' + u.username + '<br/>full name: ' + u.get_full_name() + '<br/>email: ' + u.email
							email_message(email_subject=message_subject, email_body=message_body, chapter=chapter)

						# Renders welcome page
						return HttpResponseRedirect("/welcome/" + chapter.myrobogals_url + "/")
					else:
						# Renders successfully updated profile message
						messages.success(request, message=unicode(_("Profile and settings updated!")))

						# Returns rendered page
						return HttpResponseRedirect("/profile/" + username + "/")

		# Not POST response
		else:
			# If the user is new and joining a chapter
			if join:
				formpart1 = FormPartOne(None, chapter=chapter, user_id=0)
				formpart2 = FormPartTwo(None, chapter=chapter)
				formpart3 = FormPartThree(None, chapter=chapter)
				formpart4 = FormPartFour(None, chapter=chapter)
				formpart5 = FormPartFive(None, chapter=chapter)

			# Returning the forms with prefilled information about the user fetched from the database if editing user information
			else:
				if u.tshirt:
					tshirt_id = u.tshirt.pk
				else:
					tshirt_id = None

				# Data for FormPart1
				formpart1 = FormPartOne({
					'first_name': u.first_name,
					'last_name': u.last_name,
					'username' : u.username,
					'email': u.email,
					'alt_email': u.alt_email,
					'mobile': u.mobile,
					'gender': u.gender,
					'student_number': u.student_number,
					'union_member': u.union_member,
					'police_check_number': u.police_check_number,
					'police_check_expiration': u.police_check_expiration,
					'tshirt': tshirt_id}, chapter=chapter, user_id=u.pk)

				# Data for FormPart2
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
					'email_newsletter_optin': u.email_newsletter_optin,
					'email_careers_newsletter_AU_optin': u.email_careers_newsletter_AU_optin}, chapter=chapter)
				formpart5 = FormPartFive({
					'internal_notes': u.internal_notes,
					'trained': u.trained,
					'security_check': u.security_check}, chapter=chapter)

		if 'return' in request.GET:
			return_url = request.GET['return']
		elif 'return' in request.POST:
			return_url = request.POST['return']
		else:
			return_url = ''

		chpass = (join or (request.user.is_staff and request.user != u))
		exec_fields = request.user.is_superuser or (request.user.is_staff and request.user.chapter == chapter)

		return render_to_response('profile_edit.html', {'join': join,
			'adduser': adduser,
			'chpass': chpass,
			'exec_fields': exec_fields,
			'formpart1': formpart1,
			'formpart2': formpart2,
			'formpart3': formpart3,
			'formpart4': formpart4,
			'formpart5': formpart5,
			'u': u,
			'chapter': chapter,
			'usererr': usererr,
			'pwerr': pwerr,
			'carderr': carderr,
			'new_username': new_username,
			'return': return_url},
			context_instance=RequestContext(request))
	else:
		raise Http404  # don't have permission to change


def notify_chapter(chapter, u):
	message_subject = u.get_full_name() + ' (' + u.username + ') has submitted a WWCC Number for checking'
	message_body = 'Please check the following details for ' + u.get_full_name() + ': <br /> Police check number: ' + u.police_check_number + '<br /> Expiration Date: ' + str(
		u.police_check_expiration) + '<br /> <br /> When you have verified that the volunteer has a valid card, mark them as "Passed the Police Check" on their profile from the following link: <br /> <br /> ' + 'https://myrobogals.org/profile/' + u.username + '/edit/ <br /> If they haven\'t passed the check, please re-email them at ' + u.email + ' explaining the situation'
	email_message(email_subject=message_subject, email_body=message_body, chapter=chapter)


def show_login(request):
	try:
		next = request.POST['next']
	except KeyError:
		try:
			next = request.GET['next']
		except KeyError:
			next = '/'
	return render_to_response('landing.html', {'next': next}, context_instance=RequestContext(request))

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

	print(request.POST)

	username = request.POST['username']
	password = request.POST['password']

	if email_re.match(username):
		try:
			users = User.objects.filter(email=username)
			if len(users) == 0:
				return render_to_response('login_form.html', {'username': username, 'error': 'Invalid email address or password', 'next': next}, context_instance=RequestContext(request))
			elif len(users) > 1:
				return render_to_response('login_form.html', {'username': username, 'error': 'That email address has multiple users associated with it. Please log in using your username.', 'next': next}, context_instance=RequestContext(request))
			else:
				username = users[0].username
				emaillogin = True
		except User.DoesNotExist:
			return render_to_response('login_form.html', {'username': username, 'error': 'Invalid email address or password', 'next': next}, context_instance=RequestContext(request))
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
	updateuser = forms.BooleanField(label=_('Update (instead of create) members if the username already exists'), required=False)
	ignore_email= forms.BooleanField(label=_('Ignore rows that have the same email address as an existing member'),initial=True, required=False)

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
	email_careers_newsletter_AU_optin = forms.BooleanField(label=_('Subscribe to Robogals Careers Newsletter - Australia'), required=False)

@login_required
def importusers(request, chapterurl):
    # initial value to match the default value
	updateuser=False
	ignore_email=True
	chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
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
				tmppath = '/tmp/' + chapter.myrobogals_url + request.user.username + str(time()) + ".csv"
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
				cleanform = form.cleaned_data
				request.session['welcomeemail'] = welcomeemail
				request.session['defaults'] = defaults
				request.session['updateuser'] = cleanform['updateuser']
				request.session['ignore_email']=cleanform['ignore_email']
				return render_to_response('import_users_2.html', {'tmppath': tmppath, 'filerows': filerows, 'chapter': chapter}, context_instance=RequestContext(request))
		elif request.POST['step'] == '2':
			if 'tmppath' not in request.POST:
				return HttpResponseRedirect("/chapters/" + chapterurl + "/edit/users/import/")
			tmppath = request.POST['tmppath'].replace('\\\\', '\\')
			fp = open(tmppath, 'rUb')
			filerows = csv.reader(fp)

			welcomeemail = request.session['welcomeemail']
			if welcomeemail['importaction'] == '2':
				welcomeemail = None
			defaults = request.session['defaults']
			updateuser = request.session['updateuser']
			ignore_email = request.session['ignore_email']

			try:
				(users_imported, users_updated, existing_emails, error_msg) = importcsv(filerows, welcomeemail, defaults, chapter, updateuser, ignore_email)
			except RgImportCsvException as e:
				errmsg = e.errmsg
				return render_to_response('import_users_2.html', {'tmppath': tmppath, 'filerows': filerows, 'chapter': chapter, 'errmsg': errmsg}, context_instance=RequestContext(request))

			if welcomeemail == None:
				if updateuser:
						msg = _('%d users imported.<br>Existing usernames were found for %d rows; their details have been updated.<br>%s') % (users_imported, users_updated, error_msg)
				elif ignore_email:
						msg = _('%d users imported.<br>%d rows were ignored due to members with those email addresses already existing.<br>%s') % (users_imported, existing_emails, error_msg)
				else :
						msg = _('%d users imported.<br>%s') % (users_imported, error_msg)
			else:
				if updateuser:
						msg = _('%d users imported and emailed.<br>Existing usernames were found for %d rows; their details have been updated.<br>%s') % (users_imported, users_updated, error_msg)
				elif ignore_email:
						msg = _('%d users imported and emailed.<br>%d rows were ignored due to members with those email addresses already existing.<br>%s') % (users_imported, existing_emails, error_msg)
				else :
						msg = _('%d users imported and emailed.<br>%s') % (users_imported, error_msg)
			messages.success(request, message=unicode(msg))
			del request.session['welcomeemail']
			del request.session['defaults']
			del request.session['updateuser']
			del request.session['ignore_email']
			return HttpResponseRedirect('/chapters/' + chapter.myrobogals_url + '/edit/users/')
	else:
		form = CSVUploadForm()
		welcomeform = WelcomeEmailForm(None, chapter=chapter)
		defaultsform1 = DefaultsFormOne()
		defaultsform2 = DefaultsFormTwo()
	return render_to_response('import_users_1.html', {'chapter': chapter, 'form': form, 'welcomeform': welcomeform, 'defaultsform1': defaultsform1, 'defaultsform2': defaultsform2, 'errmsg': errmsg}, context_instance=RequestContext(request))

@login_required
def exportusers(request, chapterurl):
	c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		if 'status' in request.GET:
			status = request.GET['status']
		else:
			status = '1'   # Default to student members

		if (status != '0'):
			users = MemberStatus.objects.filter(
				user__chapter=c,
				statusType__pk=status,
				status_date_end__isnull=True
			).values('user__username', 'user__first_name', 'user__last_name', 'user__email', 'user__mobile', 'user__course', 'user__university__name', 'user__student_number', 'user__alt_email', 'user__date_joined', 'user__dob', 'user__gender', 'user__uni_start', 'user__uni_end', 'user__course_type', 'user__student_type').distinct()
		else:
			users = MemberStatus.objects.filter(
				user__chapter=c,
				status_date_end__isnull=True
			).values('user__username', 'user__first_name', 'user__last_name', 'user__email', 'user__mobile', 'user__course', 'user__university__name', 'user__student_number', 'user__alt_email', 'user__date_joined', 'user__dob', 'user__gender', 'user__uni_start', 'user__uni_end', 'user__course_type', 'user__student_type').distinct()

		response = HttpResponse(content_type='text/csv')
		filename = 'robogals-' + c.myrobogals_url + '-' + str(date.today()) + '.csv'
		response['Content-Disposition'] = 'attachment; filename=' + filename
		csv_data = (('username', 'first_name', 'last_name', 'email', 'mobile', 'course', 'university', 'student_number', 'alt_email', 'date_joined', 'dob', 'gender', 'uni_start', 'uni_end', 'course_type', 'student_type'),)
		for user in users:
			csv_data = csv_data + ((user['user__username'], user['user__first_name'], user['user__last_name'], user['user__email'], user['user__mobile'], user['user__course'], user['user__university__name'], user['user__student_number'], user['user__alt_email'], user['user__date_joined'], user['user__dob'], user['user__gender'], user['user__uni_start'], user['user__uni_end'], user['user__course_type'], user['user__student_type']),)
		t = loader.get_template('csv_export.txt')
		c = Context({
			'data': csv_data,
		})
		response.write(t.render(c))
		return response
	else:
		raise Http404

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
	('gender', '0 = No answer; 1 = Male; 2 = Female; 3 = Other'),
)

EXTRA_FIELDS = (
	('course', 'Name of course/degree'),
	('uni_start', 'Date when they commenced university, in format 2007-02-28'),
	('uni_end', 'Date when they expect to complete university, in format 2011-11-30'),
	('university_id', 'ID of the university they attend. Enter -1 to use the host university of this Robogals chapter. <a href="unis/">Full list of university IDs</a>'),
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
	('email_careers_newsletter_AU_optin', 'Either \'True\' or \'False\', specifies whether this member will receive Robogals Careers Newsletter - Australia'),
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
	chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
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
				messages.success(request, message=unicode(_("Password generated and emailed")))
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
	chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
	if not (request.user.is_superuser or (request.user.is_staff and (chapter == request.user.chapter))):
		raise Http404
	unis = University.objects.all()
	return render_to_response('uni_ids_list.html', {'unis': unis}, context_instance=RequestContext(request))
