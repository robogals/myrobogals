import json
import math
import urllib
import urllib2
from time import sleep

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from myrobogals.rgmain.models import Subdivision
from myrobogals.rgteaching.forms import *
from myrobogals.rgteaching.models import (DirectorySchool, SchoolVisit, StarSchoolDirectory)
from myrobogals.rgteaching.functions import paginatorRender


# Delete a school. A school can only be deleted if it has no workshops.
@login_required
def deleteschool(request, school_id):
    if not request.user.is_staff:
        raise Http404
    chapter = request.user.chapter
    s = get_object_or_404(School, pk=school_id)
    if (s.chapter != chapter):
        raise Http404
    if request.method == 'POST':
        deleteform = DeleteForm(request.POST, user=request.user, school=s)
        if SchoolVisit.objects.filter(school=s):
            messages.success(request,
                             message=unicode(_("You cannot delete this school as it has a workshop in the database.")))
            return HttpResponseRedirect('/teaching/schools/')
        else:
            School.objects.filter(id=s.id).delete()
            messages.success(request, message=unicode(_("School sucessfully deleted.")))
            return HttpResponseRedirect('/teaching/schools/')
    else:
        deleteform = DeleteForm(None, user=request.user, school=s)
    return render_to_response('school_delete.html', {'school': s}, context_instance=RequestContext(request))


# List all this chapter's schools
@login_required
def listschools(request):
    if not request.user.is_staff:
        raise Http404
    chapter = request.user.chapter
    schools = School.objects.filter(chapter=chapter)
    return render_to_response('schools_list.html', {'chapter': chapter, 'schools': schools},
                              context_instance=RequestContext(request))


# Populate latitude-longitude in schools directory by converting the address using a Google API
@login_required
def filllatlngschdir(request):
    if request.user.is_superuser:
        schools = DirectorySchool.objects.all()
        over_query_limit = False
        for school in schools:
            sleep(0.1)
            if (school.latitude == None) or (school.longitude == None):
                data = {}
                data['address'] = school.address_street
                data[
                    'components'] = '|locality:' + school.address_city + '|administrative_area:' + school.state_code() + '|country:' + school.address_country_id + '|postal_code:' + school.address_postcode
                data['sensor'] = 'false'
                url_values = urllib.urlencode(data)
                url = 'http://maps.googleapis.com/maps/api/geocode/json'
                full_url = url + '?' + url_values
                data = urllib2.urlopen(full_url, timeout=2)
                result = json.loads(data.read())
                if result['status'] == 'OK':
                    school.latitude = result['results'][0]['geometry']['location']['lat']
                    school.longitude = result['results'][0]['geometry']['location']['lng']
                    school.save()
                elif result['status'] == 'ZERO_RESULTS':
                    pass
                elif result['status'] == 'OVER_QUERY_LIMIT':
                    msg = '- You have reached one day quota!'
                    over_query_limit = True
                    break
                elif result['status'] == 'REQUEST_DENIED':
                    pass
                elif result['status'] == 'INVALID_REQUEST':
                    pass
                else:
                    pass
            else:
                pass
        if not over_query_limit:
            msg = 'Operation successful!'
    else:
        msg = '- You can not do this!'
    messages.success(request, message=unicode(msg))
    return render_to_response('response.html', {}, context_instance=RequestContext(request))


# Schools directory. This is populated in bulk to allow Robogals chapters
# to look up schools in their area.
@login_required
def schoolsdirectory(request, chapterurl):
    c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
        raise Http404
    schools_list = DirectorySchool.objects.all()
    name = ''
    suburb = ''
    school_type = '-1'
    school_level = '-1'
    school_gender = '-1'
    starstatus = '-1'
    distance = ''
    origin = ''
    state = '1'
    if ('name' in request.GET) and (request.GET['name'] != ''):
        name = request.GET['name']
        schools_list = schools_list.filter(name__icontains=request.GET['name'])
    if ('suburb' in request.GET) and (request.GET['suburb'] != ''):
        suburb = request.GET['suburb']
        schools_list = schools_list.filter(address_city__icontains=request.GET['suburb'])
    if ('type' in request.GET) and (request.GET['type'] != '-1'):
        school_type = request.GET['type']
        schools_list = schools_list.filter(type=school_type)
    if ('level' in request.GET) and (request.GET['level'] != '-1'):
        school_level = request.GET['level']
        schools_list = schools_list.filter(level=school_level)
    if ('gender' in request.GET) and (request.GET['gender'] != '-1'):
        school_gender = request.GET['gender']
        schools_list = schools_list.filter(gender=school_gender)
    star_schools = StarSchoolDirectory.objects.filter(chapter=c).values_list('school_id', flat=True)
    if ('starstatus' in request.GET) and (request.GET['starstatus'] != '-1'):
        starstatus = request.GET['starstatus']
        if starstatus == '1':
            schools_list = schools_list.filter(id__in=star_schools)
        else:
            schools_list = schools_list.exclude(id__in=star_schools)
    sch_list = {}
    L1 = None
    G1 = None
    if ('distance' in request.GET) and (request.GET['distance'] != '') and ('origin' in request.GET) and (
        request.GET['origin'] != '') and ('state' in request.GET):
        distance = float(request.GET['distance'])
        origin = request.GET['origin']
        state = request.GET['state']
        subdiv = get_object_or_404(Subdivision, pk=state)
        try:
            data = {}
            data[
                'components'] = 'locality:' + origin + '|administrative_area:' + subdiv.code + '|country:' + subdiv.country.pk
            data['sensor'] = 'false'
            url_values = urllib.urlencode(data)
            url = 'http://maps.googleapis.com/maps/api/geocode/json'
            full_url = url + '?' + url_values
            data = urllib2.urlopen(full_url, timeout=2)
            result = json.loads(data.read())
            if result['status'] == 'OK':
                L1 = float(result['results'][0]['geometry']['location']['lat'])
                G1 = float(result['results'][0]['geometry']['location']['lng'])
                for school in schools_list:
                    if (school.latitude != None) and (school.longitude != None):
                        L2 = school.latitude
                        G2 = school.longitude
                        DG = G2 - G1
                        PI = 3.141592654
                        # Great-circle distance
                        D = 1.852 * 60.0 * (180.0 / PI) * math.acos(
                            math.sin(math.radians(L1)) * math.sin(math.radians(L2)) + math.cos(
                                math.radians(L1)) * math.cos(math.radians(L2)) * math.cos(math.radians(DG)))
                        if D <= distance:
                            sch_list[school.id] = D
                sch_list_sorted_keys = sorted(sch_list, key=sch_list.get)
                l = []
                for key in sch_list_sorted_keys:
                    l.append(schools_list.get(pk=key))
                schools_list = l
            else:
                schools_list = schools_list.filter(address_state=subdiv, address_city__iexact=origin)
                messages.success(request, message=unicode(_(
                    '- Sorry, suburb coordinate cannot be retrieved! Instead, schools within the same suburb are displayed.')))
        except:
            schools_list = schools_list.filter(address_state=subdiv, address_city__iexact=origin)
            messages.success(request, message=unicode(_(
                '- Sorry, suburb coordinate cannot be retrieved! Instead, schools within the same suburb are displayed')))

    schools = paginatorRender(request, schools_list, 26)
    copied_schools = School.objects.filter(chapter=c).values_list('name', flat=True)
    return render_to_response('schools_directory.html',
                              {'schools': schools, 'subdivision': Subdivision.objects.all().order_by('id'),
                               'DirectorySchool': DirectorySchool, 'name': name, 'suburb': suburb,
                               'school_type': int(school_type), 'school_level': int(school_level),
                               'school_gender': int(school_gender), 'starstatus': int(starstatus), 'state': int(state),
                               'star_schools': star_schools, 'chapterurl': chapterurl,
                               'return': request.path + '?' + request.META['QUERY_STRING'],
                               'copied_schools': copied_schools, 'distance': distance, 'origin': origin,
                               'sch_list': sch_list, 'L1': L1, 'G1': G1}, context_instance=RequestContext(request))


# Enable the 'star' next to a school in the schools directory
# Schools are 'starred' on a chapter-specific basis
@login_required
def starschool(request):
    if ('school_id' in request.GET) and ('chapterurl' in request.GET):
        s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
        c = get_object_or_404(Chapter, myrobogals_url__exact=request.GET['chapterurl'])
        if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
            raise Http404
        if StarSchoolDirectory.objects.filter(school=s, chapter=c):
            msg = '- The school "' + s.name + '" has been starred'
        else:
            starSchool = StarSchoolDirectory()
            starSchool.school = s
            starSchool.chapter = c
            starSchool.save()
            msg = 'The school "' + s.name + '" is starred'
        messages.success(request, message=unicode(_(msg)))
        if 'return' in request.GET:
            return HttpResponseRedirect(request.GET['return'])
        elif 'return' in request.POST:
            return HttpResponseRedirect(request.POST['return'])
        else:
            return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
    else:
        raise Http404


# Disable the 'star' next to a school in the schools directory
# Schools are 'starred' on a chapter-specific basis
@login_required
def unstarschool(request):
    if ('school_id' in request.GET) and ('chapterurl' in request.GET):
        s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
        c = get_object_or_404(Chapter, myrobogals_url__exact=request.GET['chapterurl'])
        if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
            raise Http404
        starschools = StarSchoolDirectory.objects.filter(school=s, chapter=c)
        if starschools:
            for starschool in starschools:
                starschool.delete()
            msg = 'The school "' + s.name + '" is unstarred'
        else:
            msg = '- The school "' + s.name + '" is not starred'
        messages.success(request, message=unicode(_(msg)))
        if 'return' in request.GET:
            return HttpResponseRedirect(request.GET['return'])
        elif 'return' in request.POST:
            return HttpResponseRedirect(request.POST['return'])
        else:
            return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
    else:
        raise Http404


# Copy a school from the schools directory into the chapter's school list
@login_required
def copyschool(request):
    if ('school_id' in request.GET) and ('chapterurl' in request.GET):
        s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
        c = get_object_or_404(Chapter, myrobogals_url__exact=request.GET['chapterurl'])
        if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
            raise Http404
        if School.objects.filter(chapter=c, name=s.name).count() > 0:
            msg = '- The school "' + s.name + '" is already already in your schools list'
        else:
            school = School()
            school.name = s.name
            school.chapter = c
            school.address_street = s.address_street
            school.address_city = s.address_city
            school.address_state = s.address_state.code
            school.address_postcode = s.address_postcode
            school.address_country = s.address_country
            school.contact_email = s.email
            school.contact_phone = s.phone
            school.save()
            msg = 'The school "' + s.name + '" has been added to your schools list. You can now create a workshop at this school.'
        messages.success(request, message=unicode(_(msg)))
        if 'return' in request.GET:
            return HttpResponseRedirect(request.GET['return'])
        elif 'return' in request.POST:
            return HttpResponseRedirect(request.POST['return'])
        else:
            return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
    else:
        raise Http404


# View to edit a school, or add a school if called with school_id = 0
@login_required
def editschool(request, school_id):
    chapter = request.user.chapter
    if request.user.is_staff:
        if school_id == 0:
            s = School()
            s.chapter = chapter
            new = True
        else:
            s = get_object_or_404(School, pk=school_id)
            new = False
        if (s.chapter != chapter):
            raise Http404
        if request.method == 'POST':
            formpart1 = SchoolFormPartOne(request.POST, chapter=chapter, school_id=school_id)
            formpart2 = SchoolFormPartTwo(request.POST)
            formpart3 = SchoolFormPartThree(request.POST)
            if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid():
                if school_id == 0:
                    s.chapter = chapter
                    s.creator = request.user
                data = formpart1.cleaned_data
                s.name = data['name']
                s.address_street = data['address_street']
                s.address_city = data['address_city']
                s.address_state = data['address_state']
                s.address_postcode = data['address_postcode']
                s.address_country = data['address_country']
                data = formpart2.cleaned_data
                s.contact_person = data['contact_person']
                s.contact_position = data['contact_position']
                s.contact_email = data['contact_email']
                s.contact_phone = data['contact_phone']
                data = formpart3.cleaned_data
                s.notes = data['notes']
                s.save()
                messages.success(request, message=unicode(_("School info updated")))
                return HttpResponseRedirect('/teaching/schools/')
        else:
            if school_id == 0:
                formpart1 = SchoolFormPartOne(None, chapter=chapter, school_id=school_id)
                formpart2 = SchoolFormPartTwo()
                formpart3 = SchoolFormPartThree()
            else:
                formpart1 = SchoolFormPartOne({
                    'name': s.name,
                    'address_street': s.address_street,
                    'address_city': s.address_city,
                    'address_state': s.address_state,
                    'address_postcode': s.address_postcode,
                    'address_country': s.address_country.pk}, chapter=chapter, school_id=school_id)
                formpart2 = SchoolFormPartTwo({
                    'contact_person': s.contact_person,
                    'contact_position': s.contact_position,
                    'contact_email': s.contact_email,
                    'contact_phone': s.contact_phone})
                formpart3 = SchoolFormPartThree({
                    'notes': s.notes})

        return render_to_response('school_edit.html',
                                  {'new': new, 'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3,
                                   'chapter': chapter, 'school_id': school_id},
                                  context_instance=RequestContext(request))
    else:
        raise Http404  # don't have permission to change


@login_required
def newschool(request):
    return editschool(request, 0)