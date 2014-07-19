from django.views.generic.base import TemplateView
from rest_framework import status
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth import (login as auth_login, logout as auth_logout)
from django.contrib.auth.forms import AuthenticationForm

from django.db.models import Q
import datetime
import calendar
from django.utils import timezone
from django.utils.http import http_date

#@ensure_csrf_cookie
class WebApp(TemplateView):
    template_name = "index.html"
    
def get_resource(request, resource_id):
    try:
        http_response = render(request, resource_id)
        
        # Enable caching of resources
        if request.GET.get("timeout"):
            timeout = int(request.GET.get("timeout"))
        else:
            timeout = 43200;   # 1/2 day in seconds by default
            
        http_response['Cache-Control'] = "max-age={}".format(timeout)
        http_response['Expires'] = http_date(calendar.timegm((timezone.now() + datetime.timedelta(seconds=timeout)).timetuple()))
        
        return http_response
    except TemplateDoesNotExist:
        return HttpResponse(status=404)

def set_role_id(request):
    if request.method == "POST":
        user_obj = request.user
        role_id = request.POST.get("role_id")
        
        if role_id is None:
            return HttpResponse(status=400)
        
        try:
            role_id = str(role_id)
            role_query = user_obj.role_set.filter(Q(date_start__lte=timezone.now()) & (Q(date_end__isnull=True) | Q(date_end__gte=timezone.now()))).get(pk = role_id)
            
            request.session['role_id'] = role_id
            
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=401)
            
    return HttpResponse(status=400)
        
# https://github.com/django/django/blob/master/django/contrib/auth/views.py
def login(request):                                                                                                                         
    if request.method == "POST":
        request.POST['username'] = request.POST.get("email");
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            try:
                auth_login(request, form.get_user())
            except:
                return HttpResponse(status=500)
        
            return HttpResponse(status=200)

    return HttpResponse(status=401)
    
def logout(request):
    try:
        auth_logout(request)
    except:
        return HttpResponse(status=500)
        
    return HttpResponse(status=200)
    
