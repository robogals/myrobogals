from django import template
from django.utils.dateformat import format
# from django.conf import settings
from myrobogals import settings
from django.utils.safestring import mark_safe
from myrobogals.filters.templatetags.hide_email import hide_email_filter
from myrobogals.rgmessages.models import MessagesSettings, SMSMessage, SMSRecipient, EmailFile, EmailMessage, EmailRecipient, Newsletter, NewsletterSubscriber, PendingNewsletterSubscriber, SubscriberType, SMSLengthException
import datetime
from django.utils import timezone
from myrobogals import settings

def emailpendingerror(idNoError, idError):
	if not settings.DEBUG and EmailRecipient.objects.filter(scheduled_date__lt=(timezone.now() - datetime.timedelta(hours=1)), status=0) and not settings.DEBUG:
		return '<div id="' + idError + '">'
	else:
		return '<div id="' + idNoError + '">'


register = template.Library()
register.simple_tag(emailpendingerror)
