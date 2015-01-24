# ../views.py

from django.shortcuts import render
from myrg_reports.reports import MyReport


def my_report(request):
    # Initialise the report
    template = "/myrg_webapp/templates/testreport.html"
    report = MyReport()
    context = {'report': report}

    return render(request, template, context)