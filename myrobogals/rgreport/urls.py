from django.conf.urls import url
from myrobogals.rgreport import views as report

urlpatterns = [
    url(r'^$', report.report_standard, name='standard'),
    url(r'^global/$', report.report_global, name='global'),
    url(r'^global/old/$', report.report_global_old, name='global_old'),  # TESTING PURPOSES ONLY
    url(r'^global/breakdown/(?P<chaptershorten>.+)/$', report.report_global_breakdown, name='global_breakdown'),
    url(r'^progress/$', report.progresschapter, name='progress'),
]