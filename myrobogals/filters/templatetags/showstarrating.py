from django import template
from django.utils.dateformat import format
from django.conf import settings
from django.utils.safestring import mark_safe
from myrobogals.filters.templatetags.hide_email import hide_email_filter

def showstarrating(post):
	avg_rating = post.vote_average()
	i = 1
	ret_string = ''
	while i <= avg_rating:
		ret_string = ret_string + '<img src="' + settings.MEDIA_URL + '/images/gold_star.png" alt="Star" height="12" width="12"/>'
		i = i + 1
	if (avg_rating - int(avg_rating)) >= 0.5:
		ret_string = ret_string + '<img src="' + settings.MEDIA_URL + '/images/half_star.png" alt="Star" height="12" width="12"/>'
	elif i <= 10:
		ret_string = ret_string + '<img src="' + settings.MEDIA_URL + '/images/empty_star.png" alt="Star" height="12" width="12"/>'
	i = i + 1
	while i <= 10:
		ret_string = ret_string + '<img src="' + settings.MEDIA_URL + '/images/empty_star.png" alt="Star" height="12" width="12"/>'
		i = i + 1
	return ret_string

register = template.Library()
register.filter('showstarrating', showstarrating)
