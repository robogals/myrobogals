from django.core.urlresolvers import resolve
from django.template import Library

register = Library()


@register.simple_tag
def active_nav(request, url):
    url_name = resolve(request.path).namespaces

    # No namespace available
    if not url_name:
        return ""

    # Check if namespace matches url
    url_name = url_name[0]
    if url_name == url:
        return "active"
    return ""

