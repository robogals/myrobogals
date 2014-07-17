from django.views.generic.base import TemplateView
from rest_framework import status
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.shortcuts import render

from django.contrib.auth import (login as auth_login, logout as auth_logout)
from django.contrib.auth.forms import AuthenticationForm

class WebApp(TemplateView):
    template_name = "index.html"
    
def get_resource(request, resource_id):
    try:
        return render(request, resource_id)
    except TemplateDoesNotExist:
        return HttpResponse(status=404)

    
# https://github.com/django/django/blob/master/django/contrib/auth/views.py
def login(request):                                                                                                                         
    if request.method == "POST":
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