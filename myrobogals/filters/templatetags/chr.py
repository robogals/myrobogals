from django import template
from django.utils.dateformat import format
from django.conf import settings
from django.utils.safestring import mark_safe
from myrobogals.filters.templatetags.hide_email import hide_email_filter

def chr_(value):
	return chr(value + 65)

register = template.Library()
register.filter('chr', chr_)
