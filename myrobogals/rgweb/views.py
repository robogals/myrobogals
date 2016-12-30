from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from myrobogals.rgchapter.models import Chapter

from myrobogals.rgweb.models import Website

@login_required
def websitedetails(request, chapterurl):
	c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
	if (request.user.is_staff and (request.user.chapter == c)) or request.user.is_superuser:
		websites = Website.objects.filter(site_chapter=c)
	else:
		raise Http404
	return render_to_response('website_details.html', {'websites': websites, 'c':c}, context_instance=RequestContext(request))
