from django import template
from django.utils.dateformat import format
from django.conf import settings
from django.utils.safestring import mark_safe
from myrobogals.filters.templatetags.hide_email import hide_email_filter

def blacklisted(perpetrator, forum):
	return '<a href="/forums/' + str(forum.pk) + '/unblacklistuser/' + str(perpetrator.pk) + '/">(Remove from black list)</a>' if forum.blacklist.filter(pk=perpetrator.pk) else '<a href="/forums/' + str(forum.pk) + '/blacklistuser/' + str(perpetrator.pk) + '/">(Add to black list)</a>'

register = template.Library()
register.filter('blacklisted', blacklisted)
