from django import template
from django.utils.dateformat import format
from django.conf import settings
from django.utils.safestring import mark_safe
from myrobogals.filters.templatetags.hide_email import hide_email_filter
from myrobogals.rgprofile.views import HELPINFO

def is_valid_field(field):
	for desc, fieldset in HELPINFO:
		for field_name, desc2 in fieldset:
			if field_name == field:
				return True
	return False

def valid_field(field):
	if is_valid_field(field):
		return "00ff00"
	else:
		return "ff0000"

register = template.Library()
register.simple_tag(valid_field)
