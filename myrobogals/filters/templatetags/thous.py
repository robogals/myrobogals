from django import template
import re

def thous(x):
        return re.sub(r'(\d{3})(?=\d)', r'\1,', str(x)[::-1])[::-1]

register = template.Library()
register.simple_tag(thous)
