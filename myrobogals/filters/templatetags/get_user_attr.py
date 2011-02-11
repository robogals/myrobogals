from django import template
from django.utils.dateformat import format
from django.conf import settings
from django.utils.safestring import mark_safe
from myrobogals.filters.templatetags.hide_email import hide_email_filter

def _boolean_icon(field_val):
	BOOLEAN_MAPPING = {True: 'yes', False: 'no', None: 'unknown'}
	return mark_safe(u'<img src="%simg/admin/icon-%s.gif" alt="%s" />' % (settings.ADMIN_MEDIA_PREFIX, BOOLEAN_MAPPING[field_val], field_val))

def get_user_attr(user, attr):
	val = getattr(user, attr)

	field_type = ''
	field_obj = None
	for field in user._meta.fields:
		if field.name == attr:
			field_obj = field
			field_type = field.__class__.__name__

	if attr == 'mobile':
		if val == '':
			return ''
		else:
			return '+' + val
			
	if attr == 'uni_start' or attr == 'uni_end':
		try:
			return format(val, 'M Y')
		except AttributeError:
			return ''
	
	if attr == 'email' or attr == 'alt_email':
		return hide_email_filter(val)

	if field_type == 'DateTimeField' or field_type == 'DateField':
		try:
			return format(val, 'j M Y')
		except AttributeError:
			return ''

	if field_type == 'BooleanField':
		return _boolean_icon(val)
	
	if field_obj:
		if field_obj._choices != []:
			display_func = getattr(user, 'get_' + attr + '_display')
			return display_func()

	try:
		return val()
	except:
		return str(val)

register = template.Library()
register.simple_tag(get_user_attr)
