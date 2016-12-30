from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from myrobogals.rgchapter.models import Chapter
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect, Http404

def home(request):
	return render_to_response('home.html', {'is_home': True}, context_instance=RequestContext(request))

def servererror(request):
	return render_to_response('500.html', {}, context_instance=RequestContext(request))

def welcome(request, chapterurl):
	chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
	welcome_page = chapter.welcome_page.format(chapter=chapter)
	return render_to_response('welcome.html', {'chapter': chapter, 'welcome_page': welcome_page}, context_instance=RequestContext(request))

def credits(request):
	return render_to_response('credits.html', {}, context_instance=RequestContext(request))

def support(request):
	return render_to_response('support.html', {}, context_instance=RequestContext(request))

def wiki(request):
	return render_to_response('wiki.html', {}, context_instance=RequestContext(request))

def files(request):
	return render_to_response('files.html', {}, context_instance=RequestContext(request))

# Ensure that date format strings are included in our language file
def do_nothing_dates(request):
	USELESS = [
		_('DATE_FORMAT'),
		_('DATE_FORMAT_NODAY'),
		_('DATE_FORMAT_LONG'),
		_('TIME_FORMAT'),
		_('DATETIME_FORMAT_LONG'),
		_('DATETIME_FORMAT_SPECIAL')]
	return HttpResponseRedirect('/')
