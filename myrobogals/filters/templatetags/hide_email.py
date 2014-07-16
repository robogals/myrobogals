#From http://djangosnippets.org/snippets/1349/
from django import template
from django.utils.safestring import mark_safe
import random
import re

"""
Example Usage in the template:

<p>{{ filters|hide_email }}<br />
{{ filters|hide_email:"Contact Me" }}<br />
{% hide_email "name@example.com" %}<br />
{% hide_email "name@example.com" "John Smith" %}</p>

{{ text_block|hide_all_emails|safe }}

All hidden emails are rendered as a hyperlink that is protected by
javascript and an email and name that are encoded randomly using a
hex digit or a decimal digit for each character.

Example of how a protected email is rendered:
 
<noscript>(Javascript must be enabled to see this e-mail address)</noscript>
<script type="text/javascript">// <![CDATA[
	document.write('<a href="mai'+'lto:&#106;&#x6f;&#x68;&#x6e;&#x40;&#101;&#120;&#97;&#109;&#x70;&#108;&#x65;&#46;&#x63;&#111;&#109;">&#74;&#111;&#104;&#110;&#x20;&#83;&#x6d;&#x69;&#x74;&#104;</a>')
// ]]></script>
"""

# snagged this function from http://www.djangosnippets.org/snippets/216/
def encode_string(value):
	"""
	Encode a string into it's equivalent html entity.
	
	The tag will randomly choose to represent the character as a hex digit or
	decimal digit.
	"""
	
	e_string = "" 
	for a in value:
		type = random.randint(0,1)
		if type:
			en = "&#x%x;" % ord(a)
		else:
			en = "&#%d;" % ord(a)
		e_string += en 
	return e_string


def HideEmail(email, name=None):
	
	name        = name or email
	mailto_link = u'<a href="mai\'+\'lto:%s">%s</a>' % (encode_string(email), encode_string(name))
	return u"\n<noscript>(Javascript must be enabled to see this e-mail address)</noscript>\n" \
			+'<script type="text/javascript">// <![CDATA['+"\n" \
				+"\tdocument.write('" + mailto_link + "')\n" \
					+"\t// ]]></script>\n"


class HideEmailNode(template.Node):

	def __init__(self, email, name):
		self.name = template.Variable(name)
		self.email = template.Variable(email)
	
	def render(self, context):
		name = self.name.resolve(context)
		email = self.email.resolve(context)
		return HideEmail(email, name)


def do_hide_email(parser, token):

	try:
		
		format_string = token.split_contents()
		
		# if just an email is provided then use the email address as the name
		if len(format_string) == 2:
			format_string.append(format_string[1])
					
	except:
		raise template.TemplateSyntaxError, "'%r' tag requires at least an email address or an email address and a person's name ({% hide_email user@example.com %} or {% hide_email \"user@example.com\" \"John Smith\" %})" % token.contents.split()[0]
		
	return HideEmailNode(format_string[1], format_string[2])


def hide_email_filter(email, name=None):
	
	name  = name or email
	value = HideEmail(email, name)
	return mark_safe(value)


def hide_all_emails_filter(value):
	
	# hide mailto links
	def mailto_hide_callback(matchobj):
		return HideEmail(matchobj.group(1), matchobj.group(2))

	pattern = '<a href="mailto:([\.\w-]+@[\w-]+\.[\w-]+)">([^<]+)</a>'
	value = re.sub(pattern, mailto_hide_callback, value)
	
	# hyperlink emails and hide them
	def hide_email_callback(matchobj):
		return HideEmail(matchobj.group(0), matchobj.group(0))

	pattern = "([\.\w-]+@[\w-]+\.[\w-]+)"
	value = re.sub(pattern, hide_email_callback, value)
	
	return mark_safe(value)


register = template.Library()
register.tag('hide_email', do_hide_email)
register.filter('hide_email', hide_email_filter)
register.filter('hide_all_emails', hide_all_emails_filter)
