from django import template
from django.utils.dateformat import format
from django.conf import settings
from django.utils.safestring import mark_safe
from myrobogals.filters.templatetags.hide_email import hide_email_filter
from myrobogals.rgmessages.models import MessagesSettings, SMSMessage, SMSRecipient, EmailFile, EmailMessage, EmailRecipient, Newsletter, NewsletterSubscriber, PendingNewsletterSubscriber, SubscriberType, SMSLengthException
import datetime

def emailpendingerror(idNoError, idError):
	if EmailRecipient.objects.filter(scheduled_date__lt=(datetime.datetime.now() - datetime.timedelta(hours=3)), status=0):
		return '<div id="' + idError + '">'
	else:
		return '<div id="' + idNoError + '">'


register = template.Library()
register.simple_tag(emailpendingerror)
