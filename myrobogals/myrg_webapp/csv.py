import csv
import datetime
from django.http import HttpResponse, HttpResponseForbidden
from django.template.defaultfilters import slugify
from django.db.models.loading import get_model

from myrg_users.models import RobogalsUser
from myrg_groups.models import Group
from myrg_repo.models import RepoContainer

from django.db.models.fields import FieldDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render_to_response
from django.template import RequestContext
import re


def export(qs, fields=None):
    model = qs.model
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
    writer = csv.writer(response)
    # Write headers to CSV file
    if fields:
        headers = fields
    else:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
    writer.writerow(headers)
    # Write data to CSV file
    for obj in qs:
        row = []
        for field in headers:
            if field in headers:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                row.append(val)
        writer.writerow(row)
    # Return CSV file to browser as download
    return response

def admin_list_export(request, model_name, app_label, queryset=None, fields=None, list_display=True):
    """
    Put the following line in your urls.py BEFORE your admin include
    (r'^admin/(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/csv/', 'util.csv_view.admin_list_export'),
    """
    if not request.user.is_staff:
        return HttpResponseForbidden()
    if not queryset:
        model = get_model(app_label, model_name)
        queryset = model.objects.all()
        filters = dict()
        for key, value in request.GET.items():
            if key not in ('ot', 'o'):
                filters[str(key)] = str(value)
        if len(filters):
            queryset = queryset.filter(**filters)
    if not fields:
        if list_display and len(queryset.model._meta.admin.list_display) > 1:
            fields = queryset.model._meta.admin.list_display
        else:
            fields = None
    return export(queryset, fields)
    """
    Create your own change_list.html for your admin view and put something like this in it:
    {% block object-tools %}
    <ul class="object-tools">
        <li><a href="csv/{%if request.GET%}?{{request.GET.urlencode}}{%endif%}" class="addlink">Export to CSV</a></li>
    {% if has_add_permission %}
        <li><a href="add/{% if is_popup %}?_popup=1{% endif %}" class="addlink">{% blocktrans with cl.opts.verbose_name|escape as name %}Add {{ name }}{% endblocktrans %}</a></li>
    {% endif %}
    </ul>
    {% endblock %}
    """

def convert_csv(request):
    fields = [] 
    model_name = request.POST['model']
    
    if model_name == "robogalsuser":
        app_label = "myrg_users"
    elif model_name == "group":
        app_label = "myrg_groups"
    elif model_name == "repocontainer":
        app_label = "myrg_repo"
    elif model_name == "permissionlist":
        app_label = "myrg_permissions"
                
    model = get_model(app_label, model_name)
    
    
    fields_request = request.POST['field']
    if fields_request != "":
        fieldlist = re.sub(r'\s+', '', fields_request).split(",")
    else:
        fieldlist = ""#model._meta.get_all_field_names()
    
    queryset = model.objects.all()
    for field_name in fieldlist:
        try:
            queryset.model._meta.get_field_by_name(field_name)
            fields.append(field_name)    
        except FieldDoesNotExist:
            #skip
            #queryset.model._meta.exclude(field_name)
            return Response({"detail":"`{}` is not a valid field name.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
        
    
    startdate = request.POST['startdate']
    enddate = request.POST['enddate']
    
    if startdate != "" and enddate != "":
        get_startdate = startdate.split("-")
        get_enddate = enddate.split("-")
        start_date = datetime.date(int(get_startdate[0]),int(get_startdate[1]),int(get_startdate[2]))
        end_date = datetime.date(int(get_enddate[0]),int(get_enddate[1]),int(get_enddate[2]))
        if model_name == "robogalsuser":
            queryset = queryset.filter(date_joined__range=(start_date, end_date))
        else:
            queryset = queryset.filter(date_created__range=(start_date, end_date))
    #fields = ['id']#queryset.model._meta.get_all_field_names()
    #fields = ['body', 'date_created', 'date_updated', 'id', 'role', 'service', 'tags', 'title', 'user']#
    
    return export(queryset, fields)
    #return render_to_response('csv.html',{'response': fields}, context_instance=RequestContext(request))
    

  
def convert_csv_direct(request):
    model_name = "robogalsuser"
    app_label = "myrg_users"
    model = get_model(app_label, model_name)
    queryset = model.objects.all()
    fields = ['id']#['body', 'date_created', 'date_updated', 'id', 'role', 'service', 'tags', 'title', 'user']#queryset.model._meta.get_all_field_names()
    
    return export(queryset, fields)
    #return render_to_response(
    #         'upload.html',
    #         {'response': fields})
