from myrobogals.rgprofile.models import Position
from myrobogals.rgteaching.models import SchoolVisitStats
from myrobogals.auth.models import Group, User
from myrobogals.rgmain.models import Country
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from myrobogals.auth.decorators import login_required
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect, Http404
from myrobogals.admin.widgets import FilteredSelectMultiple
from myrobogals.rgchapter.models import DisplayColumn, AwardRecipient
from myrobogals.rgchapter.models import REGION_CHOICES
from django.db import connection
from django.db.models import Q
import datetime

def list(request):
	listing = []
	superchapters = Group.objects.filter(parent=1).exclude(myrobogals_url='special')
	for superchapter in superchapters:
		if request.user.is_authenticated():
			if superchapter.status == 0 or (superchapter.status == 2 and (superchapter == request.user.chapter or request.user.is_superuser or request.user.chapter.parent == superchapter)):
				chapters_all = Group.objects.filter(parent=superchapter)
				chapters_display = []
				for chapter in chapters_all:
					if chapter.status == 0 or (chapter.status == 2 and (chapter == request.user.chapter or request.user.is_superuser)):
						chapters_display.append(chapter)
				listing.append({'super': superchapter, 'chapters': chapters_display})
		else:
			if superchapter.status == 0:
				chapters_all = Group.objects.filter(parent=superchapter)
				chapters_display = []
				for chapter in chapters_all:
					if chapter.status == 0:
						chapters_display.append(chapter)
				listing.append({'super': superchapter, 'chapters': chapters_display})
		specialch = Group.objects.filter(parent__myrobogals_url='special', status=0)
	return render_to_response('chapter_listing.html', {'listing': listing, 'specialch': specialch}, context_instance=RequestContext(request))

def joinlist(request):
	listing = []
	superchapters = Group.objects.filter(parent=1)		
	for superchapter in superchapters:
		if superchapter.status == 0:
			chapters_all = Group.objects.filter(parent=superchapter)
			chapters_display = []
			for chapter in chapters_all:
				if chapter.status == 0:
					chapters_display.append(chapter)
			listing.append({'super': superchapter, 'chapters': chapters_display})
	return render_to_response('join_listing.html', {'listing': listing}, context_instance=RequestContext(request))

def localtimes(request):
	listing = []
	globalchapter = Group.objects.get(pk=1)
	superchapters = Group.objects.filter(parent=1)		
	for superchapter in superchapters:
		if request.user.is_authenticated():
			if superchapter.status == 0 or (superchapter.status == 2 and (superchapter == request.user.chapter or request.user.is_superuser or request.user.chapter.parent == superchapter)):
				chapters_all = Group.objects.filter(parent=superchapter)
				chapters_display = []
				for chapter in chapters_all:
					if chapter.status == 0 or (chapter.status == 2 and (chapter == request.user.chapter or request.user.is_superuser)):
						chapters_display.append(chapter)
				listing.append({'super': superchapter, 'chapters': chapters_display})
		else:
			if superchapter.status == 0:
				chapters_all = Group.objects.filter(parent=superchapter)
				chapters_display = []
				for chapter in chapters_all:
					if chapter.status == 0:
						chapters_display.append(chapter)
				listing.append({'super': superchapter, 'chapters': chapters_display})
	return render_to_response('timezone_listing.html', {'listing': listing, 'globalchapter': globalchapter}, context_instance=RequestContext(request))

def detail(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	officers = Position.objects.filter(positionChapter=c).filter(position_date_end=None).order_by('positionType__rank')
	recipients = AwardRecipient.objects.filter(chapter=c)
	return render_to_response('chapter_detail.html', {'chapter': c, 'officers': officers, 'recipients': recipients}, context_instance=RequestContext(request))

@login_required
def redirtomy(request):
	return HttpResponseRedirect("/chapters/" + request.user.chapter.myrobogals_url + "/")

def awards(request):
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT YEAR FROM rgchapter_awardrecipient")
	#year_list = cursor.fetchone()
	award_dic = {}
	for row in cursor:
		award_dic[row[0]] = {}
		for i in range(len(REGION_CHOICES)):
			award_dic[row[0]][REGION_CHOICES[i][1]]= AwardRecipient.objects.filter(year=int(row[0])).filter(region=i)
	award_dic_s = sorted(award_dic.items(), reverse=True)	
	return render_to_response('chapter_award.html', {'award_dic': award_dic_s}, context_instance=RequestContext(request))

def awardsdesc(request, award_id):
	recipient = AwardRecipient.objects.get(id=award_id)
	return render_to_response('award_view.html', {'recipient': recipient}, context_instance=RequestContext(request))

# forms for editing a chapter
class FormPartOne(forms.Form):
	infobox = forms.CharField(label=_("About this chapter"), help_text = _("This is shown on your chapter page. Full HTML is allowed, including images! Please keep it somewhat professional - this is a corporate web portal, not MySpace :)"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	website_url = forms.CharField(max_length=128, label=_("Website URL"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	facebook_url = forms.CharField(max_length=128, label=_("Facebook URL"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	goal = forms.CharField(max_length=32, label=_("Goal"), help_text=_("Number of students"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	goal_start = forms.CharField(max_length=32, label=_("Goal start date"), help_text=_("The goal will be compared against girls taught since this date"), required=False, widget=forms.TextInput(attrs={'size': '30'}))

class FormPartTwo(forms.Form):
	faculty_contact = forms.CharField(max_length=64, label=_("Person"), help_text=_("e.g. Professor John Doe"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	faculty_position = forms.CharField(max_length=64, label=_("Position"), help_text=_("e.g. Associate Dean"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	faculty_department = forms.CharField(max_length=64, label=_("Department"), help_text=_("e.g. Faculty of Engineering"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	faculty_email = forms.CharField(max_length=64, label=_("Email"), help_text=_("This is kept strictly confidential. It is not shown on the chapter page."), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	faculty_phone = forms.CharField(max_length=32, label=_("Phone"), help_text=_("This is kept strictly confidential. It is not shown on the chapter page. Use international format, e.g. +61 3 8344 4000"), required=False, widget=forms.TextInput(attrs={'size': '30'}))

class FormPartThree(forms.Form):
	address = forms.CharField(label=_("Street address or PO Box"), required=False, widget=forms.Textarea(attrs={'cols': '30', 'rows': '3'}))
	city = forms.CharField(max_length=64, label=_("City/Suburb"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	state = forms.CharField(max_length=64, label=_("State/Province"), help_text=_("Use the abbreviation, e.g. 'VIC' not 'Victoria'"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	postcode = forms.CharField(max_length=16, label=_("Postcode"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)

class DPModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
    	return obj.display_name_local()

class FormPartFour(forms.Form):
	is_joinable = forms.BooleanField(label=_("Allow new members to sign up directly on myRobogals (highly recommended!)"), required=False)
	welcomepage = forms.CharField(label=_("Welcome page"), required=False, widget=forms.Textarea)
	joinpage = forms.CharField(label=_("Join page"), required=False, widget=forms.Textarea)
	display_columns = DPModelMultipleChoiceField(queryset=DisplayColumn.objects.all().order_by('order'), label=_("Columns to display"), widget=FilteredSelectMultiple(_("Columns"), False, attrs={'rows': 10}), required=True)

	# Future: use the correct language
	def __init__(self, *args, **kwargs):
		chapter=kwargs['chapter']
		del kwargs['chapter']
		super(FormPartFour, self).__init__(*args, **kwargs)
		#self.fields['list'].queryset = UserList.objects.filter(chapter=chapter)
		self.fields['welcomepage'].help_text = _("This is shown when new users have just signed up.<br>Full HTML is allowed. After saving, you can preview this page at:<br><a href=\"https://my.robogals.org/welcome/%(chapter)s/\" target=\"blank\">https://my.robogals.org/welcome/%(chapter)s/</a>") % {'chapter': chapter.myrobogals_url}
		self.fields['joinpage'].help_text = _("This is shown if people try to join, but your chapter doesn't allow<br>new members to sign up to myRobogals directly. In this case, put a<br>message here about how they <em>should</em> sign up. Full HTML is allowed.<br>After saving, and if the above checkbox is unchecked, you can preview this page at:<br><a href=\"https://my.robogals.org/join/%(chapter)s/\" target=\"blank\">https://my.robogals.org/join/%(chapter)s/</a>") % {'chapter': chapter.myrobogals_url}

class WelcomeEmailMsgField(forms.CharField):
	def clean(self, value):
		try:
			formatted = value.format(
				chapter=Group.objects.get(pk=1),
				user=User.objects.get(username='edit'),
				plaintext_password='abc123')
		except Exception:
			raise forms.ValidationError("Welcome email contains invalid field names")
		return value

class FormPartFive(forms.Form):
	welcome_email_enable = forms.BooleanField(required=False, label=_("Send a welcome email to new signups"))
	welcome_email_subject = forms.CharField(required=False, max_length=256)
	welcome_email_msg = WelcomeEmailMsgField(required=False, widget=forms.Textarea)
	welcome_email_html = forms.BooleanField(required=False)

@login_required
def progresschapter(request):
	chapter_sum = 0.0
	child_sum = 0.0
	root_sum = 0.0
	grandchildren_display = []
	listing = []
	displaycats = [0, 7]
	careertalkview = False

	if request.user.is_superuser:
		c = Group.objects.get(pk=1)
	elif request.user.is_staff:
		# Allow global and regional exec to see global progress bars
		if request.user.chapter.pk == 1:
			c = request.user.chapter
		elif request.user.chapter.parent:
			if request.user.chapter.parent.pk == 1:
				c = Group.objects.get(pk=1)
			else:
				c = request.user.chapter
		else:
			c = request.user.chapter
	else:
		raise Http404
	
	# Special exception for Robogals Rural & Regional Ambassadors programme
	# to display career talk stats in the progress bar instead of robotics workshops
	if c.pk == 20:
		careertalkview = True
		displaycats = [1,]
	
	children = Group.objects.filter(parent=c)
	for child in children:
		if child.status == 0 or (child.status == 2 and request.user.is_superuser):
			grandchildren = Group.objects.filter(parent=child)
			for grandchild in grandchildren:
				if grandchild.status == 0 or (grandchild.status == 2 and request.user.is_superuser):
					school_visits = SchoolVisitStats.objects.filter(visit__chapter=grandchild, visit__visit_start__range=[grandchild.goal_start, datetime.datetime.now()], visit_type__in=displaycats)
					for school_visit in school_visits:
						chapter_sum = chapter_sum + school_visit.num_girls_weighted()
					grandchildren_display.append((grandchild, chapter_sum))
					chapter_sum = 0.0
					school_visits = SchoolVisitStats.objects.filter(visit__chapter=grandchild, visit__visit_start__range=[child.goal_start, datetime.datetime.now()], visit_type__in=displaycats)
					for school_visit in school_visits:
						child_sum = child_sum + school_visit.num_girls_weighted()
					school_visits = SchoolVisitStats.objects.filter(visit__chapter=grandchild, visit__visit_start__range=[c.goal_start, datetime.datetime.now()], visit_type__in=displaycats)
					for school_visit in school_visits:
						root_sum = root_sum + school_visit.num_girls_weighted()
			school_visits = SchoolVisitStats.objects.filter(visit__chapter=child, visit__visit_start__range=[child.goal_start, datetime.datetime.now()], visit_type__in=displaycats)
			for school_visit in school_visits:
				child_sum = child_sum + school_visit.num_girls_weighted()
			listing.append({'child': (child, child_sum), 'grandchildren': grandchildren_display})
			grandchildren_display = []
			child_sum = 0
			school_visits = SchoolVisitStats.objects.filter(visit__chapter=child, visit__visit_start__range=[c.goal_start, datetime.datetime.now()], visit_type__in=displaycats)
			for school_visit in school_visits:
				root_sum = root_sum + school_visit.num_girls_weighted()
	school_visits = SchoolVisitStats.objects.filter(visit__chapter=c, visit__visit_start__range=[c.goal_start, datetime.datetime.now()], visit_type__in=displaycats)
	for school_visit in school_visits:
		root_sum = root_sum + school_visit.num_girls_weighted()
	return render_to_response('chapter_progress.html', {'root_chapter': (c, root_sum), 'listing': listing, 'bar_length_px': 300, 'careertalkview': careertalkview}, context_instance=RequestContext(request))

@login_required
def editchapter(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if (request.user.is_staff and request.user.chapter == c) or request.user.is_superuser:
		if request.method == 'POST':
			formpart1 = FormPartOne(request.POST)
			formpart2 = FormPartTwo(request.POST)
			formpart3 = FormPartThree(request.POST)
			formpart4 = FormPartFour(request.POST, chapter=c)
			formpart5 = FormPartFive(request.POST)
			if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid() and formpart4.is_valid() and formpart5.is_valid():
				data = formpart1.cleaned_data
				c.infobox = data['infobox']
				c.website_url = data['website_url']
				c.facebook_url = data['facebook_url']
				if data['goal'] != '':
					c.goal = data['goal']
				else:
					c.goal = None
				if data['goal_start'] != '':
					c.goal_start = data['goal_start']
				else:
					c.goal_start = None
				data = formpart2.cleaned_data
				c.faculty_contact = data['faculty_contact']
				c.faculty_position = data['faculty_position']
				c.faculty_department = data['faculty_department']
				c.faculty_email = data['faculty_email']
				c.faculty_phone = data['faculty_phone']
				data = formpart3.cleaned_data
				c.address = data['address']
				c.city = data['city']
				c.state = data['state']
				c.postcode = data['postcode']
				c.country = data['country']
				data = formpart4.cleaned_data
				c.is_joinable = data['is_joinable']
				c.welcome_page = data['welcomepage']
				c.join_page = data['joinpage']
				c.display_columns = data['display_columns']
				data = formpart5.cleaned_data
				c.welcome_email_enable = data['welcome_email_enable']
				c.welcome_email_subject = data['welcome_email_subject']
				c.welcome_email_msg = data['welcome_email_msg']
				c.welcome_email_html = data['welcome_email_html']
				c.save()
				request.user.message_set.create(message=unicode(_("Chapter info updated")))
				return HttpResponseRedirect("/chapters/" + c.myrobogals_url + "/")
		else:
			display_columns = []
			for col in c.display_columns.all():
				display_columns.append(int(col.pk))
			formpart1 = FormPartOne({
				'infobox': c.infobox,
				'website_url': c.website_url,
				'facebook_url': c.facebook_url,
				'goal': c.goal,
				'goal_start': c.goal_start})
			formpart2 = FormPartTwo({
				'faculty_contact': c.faculty_contact,
				'faculty_position': c.faculty_position,
				'faculty_department': c.faculty_department,
				'faculty_email': c.faculty_email,
				'faculty_phone': c.faculty_phone})
			if c.country:
				country = c.country.pk
			else:
				country = None
			formpart3 = FormPartThree({
				'address': c.address,
				'city': c.city,
				'state': c.state,
				'postcode': c.postcode,
				'country': country})
			formpart4 = FormPartFour({
				'is_joinable': c.is_joinable,
				'welcomepage': c.welcome_page,
				'joinpage': c.join_page,
				'display_columns': display_columns}, chapter=c)
			formpart5 = FormPartFive({
				'welcome_email_enable': c.welcome_email_enable,
				'welcome_email_subject': c.welcome_email_subject,
				'welcome_email_msg': c.welcome_email_msg,
				'welcome_email_html': c.welcome_email_html})
		return render_to_response('chapter_edit.html', {'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3, 'formpart4': formpart4, 'formpart5': formpart5, 'c': c}, context_instance=RequestContext(request))
	else:
		raise Http404
