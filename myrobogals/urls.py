from django.conf.urls.defaults import *
from myrobogals import admin, settings

admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', 'rgmain.views.home'),
	(r'^welcome/(?P<chapterurl>.+)/$', 'rgmain.views.welcome'),
	(r'^login/$', 'rgprofile.views.show_login'),
	(r'^login/process/$', 'rgprofile.views.process_login'),
	(r'^logout/$', 'auth.views.logout', {'next_page': '/'}),
	(r'^chpass/$', 'auth.views.password_change', {'template_name': 'password_change_form.html'}),
	(r'^forgotpass/done/$', 'auth.views.password_reset_done', {'template_name': 'password_reset_done.html'}),
	(r'^forgotpass/confirm/(?P<uidb36>.+)/(?P<token>.+)/$', 'auth.views.password_reset_confirm', {'template_name': 'password_reset_confirm.html'}),
	(r'^forgotpass/complete/$', 'auth.views.password_reset_complete', {'template_name': 'password_reset_complete.html'}),
	(r'^forgotpass/$', 'auth.views.password_reset', {'template_name': 'password_reset_form.html', 'email_template_name': 'password_reset_email.html'}),
	(r'^join/$', 'rgchapter.views.joinlist'),
	(r'^join/(?P<chapterurl>.+)/$', 'rgprofile.views.joinchapter'),
	(r'^newsletter/(?P<chapterurl>.+)/subscribe/$', 'rgprofile.views.newslettersub'),
	(r'^newsletter/(?P<chapterurl>.+)/subscribe/done/$', 'rgprofile.views.newslettersubdone'),
	(r'^newsletter/(?P<chapterurl>.+)/unsubscribe/$', 'rgprofile.views.newsletterunsub'),
	(r'^newsletter/(?P<chapterurl>.+)/unsubscribe/done/$', 'rgprofile.views.newsletterunsubdone'),
	(r'^profile/$', 'rgprofile.views.redirtoself'),
	(r'^profile/edit/$', 'rgprofile.views.redirtoeditself'),
	#(r'^profile/(?P<username>.+)/edit/profileimage/$', 'profileimages.views.upload_profile_image'),
	(r'^profile/(?P<username>.+)/edit/$', 'rgprofile.views.edituser'),
	(r'^profile/(?P<username>.+)/genpw/$', 'rgprofile.views.genpw'),
	(r'^profile/(?P<username>.+)/$', 'rgprofile.views.detail'),
	(r'^chapters/$', 'rgchapter.views.list'),
	(r'^chapters/awards/$', 'rgchapter.views.awards'),
	(r'^chapters/awards/(?P<award_id>\d+)/$', 'rgchapter.views.awardsdesc'),
	(r'^chapters/my/$', 'rgchapter.views.redirtomy'),
	(r'^chapters/localtimes/$', 'rgchapter.views.localtimes'),
	(r'^chapters/(?P<chapterurl>.+)/lists/(?P<list_id>\d+)/edit/$', 'rgprofile.views.edituserlist'),
	(r'^chapters/(?P<chapterurl>.+)/lists/(?P<list_id>\d+)/$', 'rgprofile.views.viewlist'),
	(r'^chapters/(?P<chapterurl>.+)/lists/add/$', 'rgprofile.views.adduserlist'),
	(r'^chapters/(?P<chapterurl>.+)/lists/$', 'rgprofile.views.listuserlists'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/import/help/unis/$', 'rgprofile.views.unilist'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/import/help/$', 'rgprofile.views.importusershelp'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/import/$', 'rgprofile.views.importusers'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/export/$', 'rgprofile.views.exportusers'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/add/$', 'rgprofile.views.adduser'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/$', 'rgprofile.views.editusers'),
	(r'^chapters/(?P<chapterurl>.+)/edit/execs/$', 'rgprofile.views.editexecs'),
	(r'^chapters/(?P<chapterurl>.+)/edit/status/$', 'rgprofile.views.editstatus'),
	(r'^chapters/(?P<chapterurl>.+)/edit/$', 'rgchapter.views.editchapter'),
	(r'^chapters/(?P<chapterurl>.+)/websitedetails/$', 'rgweb.views.websitedetails'),
	(r'^chapters/(?P<chapterurl>.+)/join/$', 'rgprofile.views.joinchapter'),
	(r'^chapters/(?P<chapterurl>.+)/$', 'rgchapter.views.detail'),
	(r'^forums/newcategory/$', 'rgforums.views.newcategory'),
	(r'^forums/newforum/$', 'rgforums.views.newforum'),
	(r'^forums/search/$', 'rgforums.views.search'),
	(r'^forums/category/delete/(?P<category_id>\d+)/$', 'rgforums.views.deletecategory'),
	(r'^forums/forum/delete/(?P<forum_id>\d+)/$', 'rgforums.views.deleteforum'),
	(r'^forums/topic/delete/(?P<topic_id>\d+)/$', 'rgforums.views.deletetopic'),
	(r'^forums/newtopic/(?P<forum_id>\d+)/$', 'rgforums.views.newtopic'),
	(r'^forums/newpost/(?P<topic_id>\d+)/$', 'rgforums.views.newpost'),
	(r'^forums/(?P<chapterurl>.+)/topic/(?P<topic_id>\d+)/$', 'rgforums.views.viewtopic'),
	(r'^forums/(?P<chapterurl>.+)/forum/(?P<forum_id>\d+)/$', 'rgforums.views.viewforum'),
	(r'^forums/(?P<chapterurl>.+)/$', 'rgforums.views.forums'),
	(r'^teaching/$', 'rgteaching.views.teachhome'),
	#(r'^teaching/availability/$', 'rgteaching.views.availability'),
	#(r'^teaching/training/$', 'rgteaching.views.training'),
	(r'^teaching/list/$', 'rgteaching.views.listvisits'),
	(r'^teaching/printlist/$', 'rgteaching.views.printlistvisits'),
	(r'^teaching/statshelp/$', 'rgteaching.views.statshelp'),
	(r'^teaching/(?P<visit_id>\d+)/$', 'rgteaching.views.viewvisit'),
	(r'^teaching/(?P<visit_id>\d+)/deletemessage/(?P<message_id>\d+)/$', 'rgteaching.views.deletemessage'),
	(r'^teaching/(?P<visit_id>\d+)/invite/$', 'rgteaching.views.invitetovisit'),
	(r'^teaching/(?P<visit_id>\d+)/email/$', 'rgteaching.views.emailvisitattendees'),
	(r'^teaching/(?P<visit_id>\d+)/edit/$', 'rgteaching.views.editvisit'),
	(r'^teaching/(?P<visit_id>\d+)/stats/$', 'rgteaching.views.stats'),
	(r'^teaching/(?P<visit_id>\d+)/statsHoursPerPerson/$', 'rgteaching.views.statsHoursPerPerson'),
	(r'^teaching/(?P<visit_id>\d+)/cancel/$', 'rgteaching.views.cancelvisit'),
	(r'^teaching/(?P<event_id>\d+)/rsvp/(?P<user_id>\d+)/(?P<rsvp_type>.+)/$', 'rgteaching.views.rsvp'),
	#(r'^teaching/(?P<event_id>\d+)/rsvp/(?P<user_id>\d+)/no/$', 'rgteaching.views.rsvpno'),
	#(r'^teaching/(?P<event_id>\d+)/rsvp/(?P<user_id>\d+)/remove/$', 'rgteaching.views.rsvpremove'),
	(r'^teaching/schools/$', 'rgteaching.views.listschools'),
	(r'^teaching/schools/(?P<school_id>\d+)/$', 'rgteaching.views.editschool'),
	(r'^teaching/schools/(?P<school_id>\d+)/delete/$', 'rgteaching.views.deleteschool'),
	(r'^teaching/schools/new/$', 'rgteaching.views.newschool'),
	(r'^teaching/new/$', 'rgteaching.views.newvisit'),
	(r'^teaching/video/$', 'rgteaching.views.videotute'),
	(r'^messages/img/(?P<msgid>\d+)/(?P<filename>.+)$', 'rgmessages.views.serveimg'),
	(r'^messages/(?P<msgid>\d+)/(?P<issue>.+)/$', 'rgmessages.views.servenewsletter'),
	(r'^messages/sms/write/$', 'rgmessages.views.writesms'),
	(r'^messages/sms/done/$', 'rgmessages.views.smsdone'),
	(r'^messages/sms/overlimit/$', 'rgmessages.views.smsoverlimit'),
	(r'^messages/email/write/$', 'rgmessages.views.writeemail'),
	(r'^messages/email/done/$', 'rgmessages.views.emaildone'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/$', 'rgmessages.views.newslettercp'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/import/$', 'rgmessages.views.importsubscribers'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/import/help/$', 'rgmessages.views.importsubscribershelp'),
	(r'^messages/history/$', 'rgmessages.views.msghistory'),
	(r'^credits/$', 'rgmain.views.credits'),
	(r'^support/$', 'rgmain.views.support'),
	(r'^wiki/$', 'rgmain.views.wiki'),
	(r'^files/$', 'rgmain.views.files'),
	(r'^api/newsletter/$', 'rgmessages.views.api'),
	(r'^api/dlr/$', 'rgmessages.views.dlrapi'),
	(r'^i18n/', include('django.conf.urls.i18n')),
	(r'^topsecretarea/', include(admin.site.urls)),
	(r'^reports/$', 'rgteaching.views.report_standard'),
	(r'^globalreports/$', 'rgteaching.views.report_global'),
	(r'^progress/$', 'rgchapter.views.progresschapter'),
	(r'^delete/user/(?P<userpk>\d+)/$', 'rgprofile.views.deleteuser'),
	(r'^tinymce/', include('tinymce.urls')),
	#(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': '/myRobogals/robogals/rgmedia/'})
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^rgmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
	)

handler500 = 'rgmain.views.servererror'
