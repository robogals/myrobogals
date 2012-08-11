from django import template
from django.utils.dateformat import format
from django.conf import settings
from django.utils.safestring import mark_safe
from myrobogals.filters.templatetags.hide_email import hide_email_filter

def showlocaltime(time, timeZone):
	if time:
		return timeZone.fromutc(time)
	else:
		return None

register = template.Library()
register.filter('showlocaltime', showlocaltime)
