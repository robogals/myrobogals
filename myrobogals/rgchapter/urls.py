from django.conf.urls import url

from myrobogals.rgchapter import views as rgchapter_views
from myrobogals.rgprofile.views import profile_chapter, profile_user
from myrobogals.rgweb import views as rgweb_views

urlpatterns = [
    url(r'^/$', rgchapter_views.list),
    url(r'^awards/$', rgchapter_views.awards),
    url(r'^awards/(?P<award_id>\d+)/$', rgchapter_views.awardsdesc),
    url(r'^my/$', rgchapter_views.redirtomy),
    url(r'^localtimes/$', rgchapter_views.localtimes),
    url(r'^(?P<chapterurl>.+)/lists/(?P<list_id>\d+)/edit/$', profile_chapter.edituserlist),
    url(r'^(?P<chapterurl>.+)/lists/(?P<list_id>\d+)/$', profile_chapter.viewlist),
    url(r'^(?P<chapterurl>.+)/lists/add/$', profile_chapter.adduserlist),
    url(r'^(?P<chapterurl>.+)/lists/$', profile_chapter.listuserlists),
    url(r'^(?P<chapterurl>.+)/edit/users/import/help/unis/$', profile_chapter.unilist),
    url(r'^(?P<chapterurl>.+)/edit/users/import/help/$', profile_chapter.importusershelp),
    url(r'^(?P<chapterurl>.+)/edit/users/import/$', profile_chapter.importusers),
    url(r'^(?P<chapterurl>.+)/edit/users/export/$', profile_chapter.exportusers),
    url(r'^(?P<chapterurl>.+)/edit/users/add/$', profile_chapter.adduser),
    url(r'^(?P<chapterurl>.+)/edit/users/$', profile_chapter.editusers, name='manage_members'),
    url(r'^(?P<chapterurl>.+)/edit/execs/$', profile_chapter.editexecs),
    url(r'^(?P<chapterurl>.+)/edit/status/$', profile_chapter.editstatus),
    url(r'^(?P<chapterurl>.+)/edit/$', rgchapter_views.editchapter, name='edit_chapter'),
    url(r'^(?P<chapterurl>.+)/websitedetails/$', rgweb_views.websitedetails),
    url(r'^(?P<chapterurl>.+)/join/$', profile_user.joinchapter),
    url(r'^(?P<chapterurl>.+)/$', rgchapter_views.detail, name='view_chapter'),
    url(r'^(?P<chapterurl>.+)/home$', rgchapter_views.home, name='home'),
]