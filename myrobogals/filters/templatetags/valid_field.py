from django import template

from myrobogals.rgprofile.views.profile_chapter import HELPINFO


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
