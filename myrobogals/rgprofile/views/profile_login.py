"""
Views related to users logging in and the appropriate redirection for non-logged in users and users that haven't filled
out a code of conduct form (if applicable)
"""

import os

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.html import format_html

from myrobogals.rgprofile.forms import LoginForm, CodeOfConductForm
from myrobogals.rgprofile.models import User
from myrobogals.settings import ROBOGALS_DIR


def show_login(request):
    try:
        next = request.POST['next']
    except KeyError:
        try:
            next = request.GET['next']
        except KeyError:
            next = '/'

    if request.method == 'POST':
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            login(request, login_form.user)
            return process_login(request, next)
    else:
        login_form = LoginForm()

    return render_to_response('landing.html', {'form': login_form, 'next': next},
                              context_instance=RequestContext(request))


def process_login(request, next):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')

    u = get_object_or_404(User, username__exact=request.user.username)

    # Only redirect if code of conduct form exists
    print(ROBOGALS_DIR + "/myrobogals/rgprofile/COCForm.txt")
    if not u.code_of_conduct and os.path.isfile(ROBOGALS_DIR + "/myrobogals/rgprofile/COCForm.txt"):
        # Redirect to accept code of conduct form on sign-in
        return HttpResponseRedirect('/code/')

    else:
        return HttpResponseRedirect(next)


@login_required()
def codeofconduct(request):
    u = get_object_or_404(User, username__exact=request.user.username)

    coc_form = CodeOfConductForm(request.POST or None)

    if request.method == 'POST':
        if coc_form.is_valid():
            data = coc_form.cleaned_data
            u.code_of_conduct = True
            u.save()
            messages.success(request, message='You have successfully accepted the code of conduct form, thanks!')
            return HttpResponseRedirect('/')

    coc_form_text = openconductfile()

    return render_to_response('code_of_conduct.html', {'form': coc_form, 'text': coc_form_text},
                              context_instance=RequestContext(request))


def openconductfile():
    try:
        f = open(ROBOGALS_DIR + "/myrobogals/rgprofile/COCForm.txt", 'r')
        f_str = f.read()
        f.close()
    except IOError:
        return None

    return format_html(f_str)