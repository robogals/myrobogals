from django.conf.urls import url

from views import quickentry, eventvisit, school, import_workshop

urlpatterns = [
    # urls for eventvisit.py functions
    url(r'^$', eventvisit.teachhome, name='home'),
    url(r'^list/$', eventvisit.listvisits),
    url(r'^printlist/$', eventvisit.printlistvisits),
    url(r'^statshelp/$', eventvisit.statshelp),
    url(r'^(?P<visit_id>\d+)/$', eventvisit.viewvisit),
    url(r'^(?P<visit_id>\d+)/deletemessage/(?P<message_id>\d+)/$', eventvisit.deletemessage),
    url(r'^(?P<visit_id>\d+)/invite/$', eventvisit.invitetovisit),
    url(r'^(?P<visit_id>\d+)/email/$', eventvisit.emailvisitattendees),
    url(r'^(?P<visit_id>\d+)/edit/$', eventvisit.editvisit),
    url(r'^(?P<visit_id>\d+)/stats/$', eventvisit.stats),
    url(r'^(?P<visit_id>\d+)/statsHoursPerPerson/$', eventvisit.statsHoursPerPerson),
    url(r'^(?P<visit_id>\d+)/cancel/$', eventvisit.cancelvisit),
    url(r'^(?P<visit_id>\d+)/reopen/$', eventvisit.reopenvisit),
    url(r'^(?P<event_id>\d+)/rsvp/(?P<user_id>\d+)/(?P<rsvp_type>.+)/$', eventvisit.rsvp),
    url(r'^(?P<school_id>\d+)/newvisit/$', eventvisit.newvisitwithschool),
    url(r'^new/$', eventvisit.newvisit),

    # urls for school.py functions
    url(r'^schools/$', school.listschools),
    url(r'^unstarschool/$', school.unstarschool),
    url(r'^starschool/$', school.starschool),
    url(r'^copyschooldir/$', school.copyschool),
    url(r'^filllatlngschdir/$', school.filllatlngschdir),
    url(r'^schoolsdirectory/(?P<chapterurl>.+)/$', school.schoolsdirectory),
    url(r'^schools/(?P<school_id>\d+)/$', school.editschool),
    url(r'^schools/(?P<school_id>\d+)/delete/$', school.deleteschool),
    url(r'^schools/new/$', school.newschool),

    # url for workshop quick entry
    url(r'^quickentry/$', quickentry.instantvisit),

    # url for importing workshops
    url(r'^import/$', import_workshop.ImportWorkshopView.as_view(), name='import_workshops'),
    url(r'^import/download/$', import_workshop.download, name='download')
]
