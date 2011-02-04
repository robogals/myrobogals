from myrobogals.rgprofile.models import Position
from myrobogals.auth.models import Group
from myrobogals.rgprofile.usermodels import Country
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from myrobogals.auth.decorators import login_required
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect, Http404

def list(request):
	listing = []
	superchapters = Group.objects.filter(parent=1)		
	for superchapter in superchapters:
		chapters = Group.objects.filter(parent=superchapter)
		listing.append({'super': superchapter, 'chapters': chapters})
	return render_to_response('chapter_listing.html', {'listing': listing}, context_instance=RequestContext(request))

def joinlist(request):
	listing = []
	superchapters = Group.objects.filter(parent=1)		
	for superchapter in superchapters:
		chapters = Group.objects.filter(parent=superchapter)
		listing.append({'super': superchapter, 'chapters': chapters})
	return render_to_response('join_listing.html', {'listing': listing}, context_instance=RequestContext(request))

def localtimes(request):
	listing = []
	globalchapter = Group.objects.get(pk=1)
	superchapters = Group.objects.filter(parent=1)
	for superchapter in superchapters:
		chapters = Group.objects.filter(parent=superchapter)
		listing.append({'super': superchapter, 'chapters': chapters})
	return render_to_response('timezone_listing.html', {'listing': listing, 'globalchapter': globalchapter}, context_instance=RequestContext(request))

def detail(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	officers = Position.objects.filter(positionChapter=c).filter(position_date_end=None).order_by('positionType__rank')
	return render_to_response('chapter_detail.html', {'chapter': c, 'officers': officers}, context_instance=RequestContext(request))

@login_required
def redirtomy(request):
	return HttpResponseRedirect("/chapters/" + request.user.chapter().myrobogals_url + "/")

# forms for editing a chapter
class FormPartOne(forms.Form):
	infobox = forms.CharField(label=_("About this chapter"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	website_url = forms.CharField(max_length=128, label=_("Website URL"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
	facebook_url = forms.CharField(max_length=128, label=_("Facebook URL"), required=False, widget=forms.TextInput(attrs={'size': '30'}))

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

class FormPartFour(forms.Form):
	is_joinable = forms.BooleanField(label=_("Accept new members through website (if this is unchecked, new members can only be added by exec)"), required=False)
	emailtext = forms.CharField(label=_("Default email reminder"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
	smstext = forms.CharField(label=_("Default SMS reminder"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))

@login_required
def editchapter(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	if (request.user.is_staff and request.user.chapter() == c):
		if request.method == 'POST':
			formpart1 = FormPartOne(request.POST)
			formpart2 = FormPartTwo(request.POST)
			formpart3 = FormPartThree(request.POST)
			formpart4 = FormPartFour(request.POST)
			if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid() and formpart4.is_valid():
				data = formpart1.cleaned_data
				c.infobox = data['infobox']
				c.website_url = data['website_url']
				c.facebook_url = data['facebook_url']
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
				c.emailtext = data['emailtext']
				c.smstext = data['smstext']
				c.save()
				request.user.message_set.create(message=unicode(_("Chapter info updated")))
				return HttpResponseRedirect("/chapters/" + c.myrobogals_url + "/")
		else:
			formpart1 = FormPartOne({
				'infobox': c.infobox,
				'website_url': c.website_url,
				'facebook_url': c.facebook_url})
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
				'emailtext': c.emailtext,
				'smstext': c.smstext})
		return render_to_response('chapter_edit.html', {'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3, 'formpart4': formpart4, 'c': c}, context_instance=RequestContext(request))
	else:
		raise Http404
