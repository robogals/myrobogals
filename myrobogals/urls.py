from django.conf.urls.defaults import *
from myrobogals import admin, settings

admin.autodiscover()

urlpatterns = patterns('',
	# Home
	(r'^$', 'rgmain.views.home'),

	# User functions
	(r'^login/$', 'rgprofile.views.show_login'),
	(r'^login/process/$', 'rgprofile.views.process_login'),
	(r'^logout/$', 'auth.views.logout', {'next_page': '/'}),
	(r'^chpass/$', 'auth.views.password_change', {'template_name': 'password_change_form.html'}),
	(r'^forgotpass/done/$', 'auth.views.password_reset_done', {'template_name': 'password_reset_done.html'}),
	(r'^forgotpass/confirm/(?P<uidb36>.+)/(?P<token>.+)/$', 'auth.views.password_reset_confirm', {'template_name': 'password_reset_confirm.html'}),
	(r'^forgotpass/complete/$', 'auth.views.password_reset_complete', {'template_name': 'password_reset_complete.html'}),
	(r'^forgotpass/$', 'auth.views.password_reset', {'template_name': 'password_reset_form.html', 'email_template_name': 'password_reset_email.html'}),
	(r'^unsubscribe/(?P<uidb36>.+)/(?P<token>.+)/(?P<step>\d)/$', 'auth.views.unsubscribe'),
	(r'^join/$', 'rgchapter.views.joinlist'),
	(r'^join/(?P<chapterurl>.+)/$', 'rgprofile.views.joinchapter'),
	(r'^welcome/(?P<chapterurl>.+)/$', 'rgmain.views.welcome'),

	# Profile menu
	(r'^profile/$', 'rgprofile.views.redirtoself'),
	(r'^profile/contactdirectory/$', 'rgprofile.views.contactdirectory'),
	(r'^profile/edit/$', 'rgprofile.views.redirtoeditself'),
	(r'^profile/mobverify/$', 'rgprofile.views.mobverify'),
	#(r'^profile/(?P<username>.+)/edit/profileimage/$', 'profileimages.views.upload_profile_image'),
	(r'^profile/(?P<username>.+)/edit/$', 'rgprofile.views.edituser'),
	(r'^profile/(?P<username>.+)/genpw/$', 'rgprofile.views.genpw'),
	(r'^profile/(?P<username>.+)/$', 'rgprofile.views.detail'),
	
	# Chapters menu
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
	(r'^conferences/$', 'rgconf.views.home'),
	(r'^conferences/(?P<conf_id>\d+)/$', 'rgconf.views.rsvplist'),
	(r'^conferences/(?P<conf_id>\d+)/nametags\.csv$', 'rgconf.views.nametagscsv'),
	(r'^conferences/(?P<conf_id>\d+)/email/$', 'rgconf.views.rsvpemail'),
	(r'^conferences/(?P<conf_id>\d+)/(?P<username>.+)/rsvp/$', 'rgconf.views.editrsvp'),
	(r'^conferences/(?P<conf_id>\d+)/(?P<username>.+)/invoice/$', 'rgconf.views.showinvoice'),

	# Forums
	(r'^forums/newcategory/$', 'rgforums.views.newcategory'),
	(r'^forums/newforum/$', 'rgforums.views.newforum'),
	(r'^forums/stickytopic/$', 'rgforums.views.stickytopic'),
	(r'^forums/setmaxuploadfilesize/$', 'rgforums.views.setmaxuploadfilesize'),
	(r'^forums/category/delete/(?P<category_id>\d+)/$', 'rgforums.views.deletecategory'),
	(r'^forums/forum/delete/(?P<forum_id>\d+)/$', 'rgforums.views.deleteforum'),
	(r'^forums/topic/delete/(?P<topic_id>\d+)/$', 'rgforums.views.deletetopic'),
	(r'^forums/post/delete/(?P<post_id>\d+)/$', 'rgforums.views.deletepost'),
	(r'^forums/post/fileoffenses/(?P<post_id>\d+)/$', 'rgforums.views.fileoffenses'),
	(r'^forums/showforumoffenses/(?P<forum_id>\d+)/$', 'rgforums.views.showforumoffenses'),
	(r'^forums/unwatchforum/(?P<forum_id>\d+)/$', 'rgforums.views.unwatchforum'),
	(r'^forums/watchforum/(?P<forum_id>\d+)/$', 'rgforums.views.watchforum'),
	(r'^forums/unwatchtopic/(?P<topic_id>\d+)/$', 'rgforums.views.unwatchtopic'),
	(r'^forums/watchtopic/(?P<topic_id>\d+)/$', 'rgforums.views.watchtopic'),
	(r'^forums/unwatchalltopics/$', 'rgforums.views.unwatchalltopics'),
	(r'^forums/watchmytopics/$', 'rgforums.views.watchtopicwithmyposts'),
	(r'^forums/unwatchall/(?P<uidb36>.+)/(?P<token>.+)/(?P<step>\d)/$', 'rgforums.views.unwatchall'),
	(r'^forums/search/(?P<chapterurl>.+)/$', 'rgforums.views.search'),
	(r'^forums/newtopic/(?P<forum_id>\d+)/$', 'rgforums.views.newtopic'),
	(r'^forums/newpost/(?P<topic_id>\d+)/$', 'rgforums.views.newpost'),
	(r'^forums/editpost/(?P<post_id>\d+)/$', 'rgforums.views.editpost'),
	(r'^forums/filevote/(?P<post_id>\d+)/(?P<score>\d+)/$', 'rgforums.views.filevote'),
	(r'^forums/deletefile/(?P<post_id>\d+)/$', 'rgforums.views.deletefile'),
	(r'^forums/downloadpostfile/(?P<post_id>\d+)/$', 'rgforums.views.downloadpostfile'),
	(r'^forums/editforum/(?P<forum_id>\d+)/$', 'rgforums.views.editforum'),
	(r'^forums/topic/(?P<topic_id>\d+)/$', 'rgforums.views.viewtopic'),
	(r'^forums/forum/(?P<forum_id>\d+)/$', 'rgforums.views.viewforum'),
	(r'^forums/$', 'rgforums.views.forums'),
	(r'^forums/(?P<forum_id>\d+)/blacklistuser/(?P<user_id>\d+)/$', 'rgforums.views.blacklistuser'),
	(r'^forums/(?P<forum_id>\d+)/unblacklistuser/(?P<user_id>\d+)/$', 'rgforums.views.unblacklistuser'),

	# Workshops menu
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
	(r'^teaching/(?P<visit_id>\d+)/reopen/$', 'rgteaching.views.reopenvisit'),
	(r'^teaching/(?P<event_id>\d+)/rsvp/(?P<user_id>\d+)/(?P<rsvp_type>.+)/$', 'rgteaching.views.rsvp'),
	(r'^teaching/schools/$', 'rgteaching.views.listschools'),
	(r'^teaching/unstarschool/$', 'rgteaching.views.unstarschool'),
	(r'^teaching/starschool/$', 'rgteaching.views.starschool'),
	(r'^teaching/copyschooldir/$', 'rgteaching.views.copyschool'),
	(r'^teaching/filllatlngschdir/$', 'rgteaching.views.filllatlngschdir'),
	(r'^teaching/schoolsdirectory/(?P<chapterurl>.+)/$', 'rgteaching.views.schoolsdirectory'),
	(r'^teaching/schools/(?P<school_id>\d+)/$', 'rgteaching.views.editschool'),
	(r'^teaching/schools/(?P<school_id>\d+)/delete/$', 'rgteaching.views.deleteschool'),
	(r'^teaching/schools/new/$', 'rgteaching.views.newschool'),
	(r'^teaching/(?P<school_id>\d+)/newvisit/$', 'rgteaching.views.newvisitwithschool'),
	(r'^teaching/new/$', 'rgteaching.views.newvisit'),
	(r'^teaching/video/$', 'rgteaching.views.videotute'),
	(r'^reports/$', 'rgteaching.views.report_standard'),
	(r'^globalreports/$', 'rgteaching.views.report_global'),
	(r'^progress/$', 'rgchapter.views.progresschapter'),

	# Email & SMS menu
	(r'^messages/img/(?P<msgid>\d+)/(?P<filename>.+)$', 'rgmessages.views.serveimg'),
	(r'^messages/(?P<msgid>\d+)/(?P<issue>.+)/$', 'rgmessages.views.servenewsletter'),
	(r'^messages/sms/write/$', 'rgmessages.views.writesms'),
	(r'^messages/sms/done/$', 'rgmessages.views.smsdone'),
	(r'^messages/sms/overlimit/$', 'rgmessages.views.smsoverlimit'),
	(r'^messages/email/write/$', 'rgmessages.views.writeemail'),
	(r'^messages/setmaxuploadfilesize/$', 'rgmessages.views.setmaxuploadfilesize'),
	(r'^messages/email/done/$', 'rgmessages.views.emaildone'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/$', 'rgmessages.views.newslettercp'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/import/$', 'rgmessages.views.importsubscribers'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/import/help/$', 'rgmessages.views.importsubscribershelp'),
	(r'^messages/emailrecipients/(?P<email_id>\d+)/$', 'rgmessages.views.emailrecipients'),
	(r'^messages/smsrecipients/(?P<sms_id>\d+)/$', 'rgmessages.views.smsrecipients'),
	(r'^messages/showemail/(?P<email_id>\d+)/$', 'rgmessages.views.showemail'),
	(r'^messages/downloademailfile/(?P<email_id>\d+)/(?P<file_name>.+)/$', 'rgmessages.views.downloademailfile'),
	(r'^messages/history/$', 'rgmessages.views.msghistory'),
	
	# Wiki
	(r'^wiki/$', 'rgmain.views.wiki'),

	# Static pages
	(r'^credits/$', 'rgmain.views.credits'),
	(r'^support/$', 'rgmain.views.support'),

	# Chapter-based newsletter API
	(r'^newsletter/(?P<chapterurl>.+)/subscribe/$', 'rgprofile.views.newslettersub'),
	(r'^newsletter/(?P<chapterurl>.+)/subscribe/done/$', 'rgprofile.views.newslettersubdone'),
	(r'^newsletter/(?P<chapterurl>.+)/unsubscribe/$', 'rgprofile.views.newsletterunsub'),
	(r'^newsletter/(?P<chapterurl>.+)/unsubscribe/done/$', 'rgprofile.views.newsletterunsubdone'),
	# Amplifier newsletter API
	(r'^api/newsletter/$', 'rgmessages.views.api'),
	# SMSGlobal delivery receipts API
	(r'^api/dlr/$', 'rgmessages.views.dlrapi'),
	# Google Maps KML API
	(r'^api/robogals-chapter-map.kml', 'rgchapter.views.chaptermap'),
	# Delete user API
	(r'^delete/user/(?P<userpk>\d+)/$', 'rgprofile.views.deleteuser'),

	# i18n helpers
	(r'^i18n/', include('django.conf.urls.i18n')),
	# TinyMCE helpers
	(r'^tinymce/', include('tinymce.urls')),
	
	# Admin site
	(r'^topsecretarea/', include(admin.site.urls)),
)

# If running the local development server - this will serve the media files through it too
if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^rgmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
	)

# Custom view for 500 Internal Server Error
handler500 = 'rgmain.views.servererror'
