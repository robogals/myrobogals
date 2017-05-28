# https://djangosnippets.org/snippets/2599/
from functools import wraps

from django.http import Http404


def staff_or_404(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, raising a 404 if necessary.
    """
    def _checklogin(request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            # The user is valid. Continue to the admin page.
            return view_func(request, *args, **kwargs)

        else:
            raise Http404

    return wraps(view_func)(_checklogin)