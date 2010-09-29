def mediaurl(request):
	from myrobogals import settings
	return {'media_url': settings.MEDIA_URL }
