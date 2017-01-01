from django.conf.urls import patterns, url, include
from myrobogals import settings
from django.contrib import admin

urlpatterns = patterns('',
	# Home
	(r'^$', 'myrobogals.rgmain.views.home'),

	# User functions
	(r'^login/$', 'myrobogals.rgprofile.views.show_login'),
	(r'^login/process/$', 'myrobogals.rgprofile.views.process_login'),
	(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
	(r'^chpass/$', 'django.contrib.auth.views.password_change', {'template_name': 'password_change_form.html', 'post_change_redirect': '/profile'}),
	url(r'^forgotpass/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'password_reset_done.html'}, name='password_reset_done'),
	(r'^forgotpass/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name': 'password_reset_confirm.html'}),
	(r'^forgotpass/complete/$', 'django.contrib.auth.views.password_reset_complete', {'template_name': 'password_reset_complete.html'}),
	(r'^forgotpass/$', 'django.contrib.auth.views.password_reset', {'template_name': 'password_reset_form.html', 'email_template_name': 'password_reset_email.html'}),
	#(r'^unsubscribe/(?P<uidb36>.+)/(?P<token>.+)/(?P<step>\d)/$', 'django.contrib.auth.views.unsubscribe'),
	(r'^join/$', 'myrobogals.rgchapter.views.joinlist'),
	(r'^join/(?P<chapterurl>.+)/$', 'myrobogals.rgprofile.views.joinchapter'),
	(r'^welcome/(?P<chapterurl>.+)/$', 'myrobogals.rgmain.views.welcome'),

	# Profile menu
	(r'^profile/$', 'myrobogals.rgprofile.views.redirtoself'),
	(r'^profile/contactdirectory/$', 'myrobogals.rgprofile.views.contactdirectory'),
	(r'^profile/edit/$', 'myrobogals.rgprofile.views.redirtoeditself'),
	(r'^profile/mobverify/$', 'myrobogals.rgprofile.views.mobverify'),
	#(r'^profile/(?P<username>.+)/edit/profileimage/$', 'profileimages.views.upload_profile_image'),
	(r'^profile/(?P<username>.+)/edit/$', 'myrobogals.rgprofile.views.edituser'),
	(r'^profile/(?P<username>.+)/genpw/$', 'myrobogals.rgprofile.views.genpw'),
	(r'^profile/(?P<username>.+)/$', 'myrobogals.rgprofile.views.detail'),
	
	# Chapters menu
	(r'^chapters/$', 'myrobogals.rgchapter.views.list'),
	(r'^chapters/awards/$', 'myrobogals.rgchapter.views.awards'),
	(r'^chapters/awards/(?P<award_id>\d+)/$', 'myrobogals.rgchapter.views.awardsdesc'),
	(r'^chapters/my/$', 'myrobogals.rgchapter.views.redirtomy'),
	(r'^chapters/localtimes/$', 'myrobogals.rgchapter.views.localtimes'),
	(r'^chapters/(?P<chapterurl>.+)/lists/(?P<list_id>\d+)/edit/$', 'myrobogals.rgprofile.views.edituserlist'),
	(r'^chapters/(?P<chapterurl>.+)/lists/(?P<list_id>\d+)/$', 'myrobogals.rgprofile.views.viewlist'),
	(r'^chapters/(?P<chapterurl>.+)/lists/add/$', 'myrobogals.rgprofile.views.adduserlist'),
	(r'^chapters/(?P<chapterurl>.+)/lists/$', 'myrobogals.rgprofile.views.listuserlists'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/import/help/unis/$', 'myrobogals.rgprofile.views.unilist'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/import/help/$', 'myrobogals.rgprofile.views.importusershelp'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/import/$', 'myrobogals.rgprofile.views.importusers'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/export/$', 'myrobogals.rgprofile.views.exportusers'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/add/$', 'myrobogals.rgprofile.views.adduser'),
	(r'^chapters/(?P<chapterurl>.+)/edit/users/$', 'myrobogals.rgprofile.views.editusers'),
	(r'^chapters/(?P<chapterurl>.+)/edit/execs/$', 'myrobogals.rgprofile.views.editexecs'),
	(r'^chapters/(?P<chapterurl>.+)/edit/status/$', 'myrobogals.rgprofile.views.editstatus'),
	(r'^chapters/(?P<chapterurl>.+)/edit/$', 'myrobogals.rgchapter.views.editchapter'),
	(r'^chapters/(?P<chapterurl>.+)/websitedetails/$', 'myrobogals.rgweb.views.websitedetails'),
	(r'^chapters/(?P<chapterurl>.+)/join/$', 'myrobogals.rgprofile.views.joinchapter'),
	(r'^chapters/(?P<chapterurl>.+)/$', 'myrobogals.rgchapter.views.detail'),
	(r'^conferences/$', 'myrobogals.rgconf.views.home'),
	(r'^conferences/(?P<conf_id>\d+)/$', 'myrobogals.rgconf.views.rsvplist'),
	(r'^conferences/(?P<conf_id>\d+)/nametags\.csv$', 'myrobogals.rgconf.views.nametagscsv'),
	(r'^conferences/(?P<conf_id>\d+)/email/$', 'myrobogals.rgconf.views.rsvpemail'),
	(r'^conferences/(?P<conf_id>\d+)/(?P<username>.+)/rsvp/$', 'myrobogals.rgconf.views.editrsvp'),
	(r'^conferences/(?P<conf_id>\d+)/(?P<username>.+)/invoice/$', 'myrobogals.rgconf.views.showinvoice'),

	# Forums
	(r'^forums/newcategory/$', 'myrobogals.rgforums.views.newcategory'),
	(r'^forums/newforum/$', 'myrobogals.rgforums.views.newforum'),
	(r'^forums/stickytopic/$', 'myrobogals.rgforums.views.stickytopic'),
	(r'^forums/setmaxuploadfilesize/$', 'myrobogals.rgforums.views.setmaxuploadfilesize'),
	(r'^forums/category/delete/(?P<category_id>\d+)/$', 'myrobogals.rgforums.views.deletecategory'),
	(r'^forums/forum/delete/(?P<forum_id>\d+)/$', 'myrobogals.rgforums.views.deleteforum'),
	(r'^forums/topic/delete/(?P<topic_id>\d+)/$', 'myrobogals.rgforums.views.deletetopic'),
	(r'^forums/post/delete/(?P<post_id>\d+)/$', 'myrobogals.rgforums.views.deletepost'),
	(r'^forums/post/fileoffenses/(?P<post_id>\d+)/$', 'myrobogals.rgforums.views.fileoffenses'),
	(r'^forums/showforumoffenses/(?P<forum_id>\d+)/$', 'myrobogals.rgforums.views.showforumoffenses'),
	(r'^forums/unwatchforum/(?P<forum_id>\d+)/$', 'myrobogals.rgforums.views.unwatchforum'),
	(r'^forums/watchforum/(?P<forum_id>\d+)/$', 'myrobogals.rgforums.views.watchforum'),
	(r'^forums/unwatchtopic/(?P<topic_id>\d+)/$', 'myrobogals.rgforums.views.unwatchtopic'),
	(r'^forums/watchtopic/(?P<topic_id>\d+)/$', 'myrobogals.rgforums.views.watchtopic'),
	(r'^forums/unwatchalltopics/$', 'myrobogals.rgforums.views.unwatchalltopics'),
	(r'^forums/watchmytopics/$', 'myrobogals.rgforums.views.watchtopicwithmyposts'),
	(r'^forums/unwatchall/(?P<uidb36>.+)/(?P<token>.+)/(?P<step>\d)/$', 'myrobogals.rgforums.views.unwatchall'),
	(r'^forums/search/(?P<chapterurl>.+)/$', 'myrobogals.rgforums.views.search'),
	(r'^forums/newtopic/(?P<forum_id>\d+)/$', 'myrobogals.rgforums.views.newtopic'),
	(r'^forums/newpost/(?P<topic_id>\d+)/$', 'myrobogals.rgforums.views.newpost'),
	(r'^forums/editpost/(?P<post_id>\d+)/$', 'myrobogals.rgforums.views.editpost'),
	(r'^forums/upvote/(?P<post_id>\d+)/$', 'myrobogals.rgforums.views.topicupvote'),
	(r'^forums/undoupvote/(?P<post_id>\d+)/$', 'myrobogals.rgforums.views.topicundoupvote'),
	(r'^forums/deletefile/(?P<post_id>\d+)/(?P<file_id>\d+)/$', 'myrobogals.rgforums.views.deletefile'),
	(r'^forums/downloadpostfile/(?P<post_id>\d+)/(?P<file_id>\d+)/$', 'myrobogals.rgforums.views.downloadpostfile'),
	(r'^forums/editforum/(?P<forum_id>\d+)/$', 'myrobogals.rgforums.views.editforum'),
	(r'^forums/topic/(?P<topic_id>\d+)/$', 'myrobogals.rgforums.views.viewtopic'),
	(r'^forums/forum/(?P<forum_id>\d+)/$', 'myrobogals.rgforums.views.viewforum'),
	(r'^forums/$', 'myrobogals.rgforums.views.forums'),
	(r'^forums/(?P<forum_id>\d+)/blacklistuser/(?P<user_id>\d+)/$', 'myrobogals.rgforums.views.blacklistuser'),
	(r'^forums/(?P<forum_id>\d+)/unblacklistuser/(?P<user_id>\d+)/$', 'myrobogals.rgforums.views.unblacklistuser'),

	# Workshops menu
	(r'^teaching/$', 'myrobogals.rgteaching.views.teachhome'),
	#(r'^teaching/availability/$', 'myrobogals.rgteaching.views.availability'),
	#(r'^teaching/training/$', 'myrobogals.rgteaching.views.training'),
	(r'^teaching/list/$', 'myrobogals.rgteaching.views.listvisits'),
	(r'^teaching/printlist/$', 'myrobogals.rgteaching.views.printlistvisits'),
	(r'^teaching/statshelp/$', 'myrobogals.rgteaching.views.statshelp'),
	(r'^teaching/(?P<visit_id>\d+)/$', 'myrobogals.rgteaching.views.viewvisit'),
	(r'^teaching/(?P<visit_id>\d+)/deletemessage/(?P<message_id>\d+)/$', 'myrobogals.rgteaching.views.deletemessage'),
	(r'^teaching/(?P<visit_id>\d+)/invite/$', 'myrobogals.rgteaching.views.invitetovisit'),
	(r'^teaching/(?P<visit_id>\d+)/email/$', 'myrobogals.rgteaching.views.emailvisitattendees'),
	(r'^teaching/(?P<visit_id>\d+)/edit/$', 'myrobogals.rgteaching.views.editvisit'),
	(r'^teaching/(?P<visit_id>\d+)/stats/$', 'myrobogals.rgteaching.views.stats'),
	(r'^teaching/(?P<visit_id>\d+)/statsHoursPerPerson/$', 'myrobogals.rgteaching.views.statsHoursPerPerson'),
	(r'^teaching/(?P<visit_id>\d+)/cancel/$', 'myrobogals.rgteaching.views.cancelvisit'),
	(r'^teaching/(?P<visit_id>\d+)/reopen/$', 'myrobogals.rgteaching.views.reopenvisit'),
	(r'^teaching/(?P<event_id>\d+)/rsvp/(?P<user_id>\d+)/(?P<rsvp_type>.+)/$', 'myrobogals.rgteaching.views.rsvp'),
	(r'^teaching/schools/$', 'myrobogals.rgteaching.views.listschools'),
	(r'^teaching/unstarschool/$', 'myrobogals.rgteaching.views.unstarschool'),
	(r'^teaching/starschool/$', 'myrobogals.rgteaching.views.starschool'),
	(r'^teaching/copyschooldir/$', 'myrobogals.rgteaching.views.copyschool'),
	(r'^teaching/filllatlngschdir/$', 'myrobogals.rgteaching.views.filllatlngschdir'),
	(r'^teaching/schoolsdirectory/(?P<chapterurl>.+)/$', 'myrobogals.rgteaching.views.schoolsdirectory'),
	(r'^teaching/schools/(?P<school_id>\d+)/$', 'myrobogals.rgteaching.views.editschool'),
	(r'^teaching/schools/(?P<school_id>\d+)/delete/$', 'myrobogals.rgteaching.views.deleteschool'),
	(r'^teaching/schools/new/$', 'myrobogals.rgteaching.views.newschool'),
	(r'^teaching/(?P<school_id>\d+)/newvisit/$', 'myrobogals.rgteaching.views.newvisitwithschool'),
	(r'^teaching/new/$', 'myrobogals.rgteaching.views.newvisit'),
	(r'^reports/$', 'myrobogals.rgteaching.views.report_standard'),
	(r'^globalreports/$', 'myrobogals.rgteaching.views.report_global'),
	(r'^globalreports/breakdown/(?P<chaptershorten>.+)/$', 'myrobogals.rgteaching.views.report_global_breakdown'),
	(r'^progress/$', 'myrobogals.rgchapter.views.progresschapter'),

	# Email & SMS menu
	(r'^messages/img/(?P<msgid>\d+)/(?P<filename>.+)$', 'myrobogals.rgmessages.views.serveimg'),
	(r'^messages/(?P<msgid>\d+)/(?P<issue>.+)/$', 'myrobogals.rgmessages.views.servenewsletter'),
	(r'^messages/sms/write/$', 'myrobogals.rgmessages.views.writesms'),
	(r'^messages/sms/done/$', 'myrobogals.rgmessages.views.smsdone'),
	(r'^messages/sms/overlimit/$', 'myrobogals.rgmessages.views.smsoverlimit'),
	(r'^messages/email/write/$', 'myrobogals.rgmessages.views.writeemail'),
	(r'^messages/setmaxuploadfilesize/$', 'myrobogals.rgmessages.views.setmaxuploadfilesize'),
	(r'^messages/email/done/$', 'myrobogals.rgmessages.views.emaildone'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/$', 'myrobogals.rgmessages.views.newslettercp'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/import/$', 'myrobogals.rgmessages.views.importsubscribers'),
	(r'^messages/newsletters/(?P<newsletter_id>\d+)/import/help/$', 'myrobogals.rgmessages.views.importsubscribershelp'),
	(r'^messages/emailrecipients/(?P<email_id>\d+)/$', 'myrobogals.rgmessages.views.emailrecipients'),
	(r'^messages/smsrecipients/(?P<sms_id>\d+)/$', 'myrobogals.rgmessages.views.smsrecipients'),
	(r'^messages/showemail/(?P<email_id>\d+)/$', 'myrobogals.rgmessages.views.showemail'),
	(r'^messages/downloademailfile/(?P<email_id>\d+)/(?P<file_name>.+)/$', 'myrobogals.rgmessages.views.downloademailfile'),
	(r'^messages/history/$', 'myrobogals.rgmessages.views.msghistory'),
	(r'^messages/previewemail/$', 'myrobogals.rgmessages.views.previewemail'),
	
	# Wiki
	(r'^wiki/$', 'myrobogals.rgmain.views.wiki'),

	# Static pages
	(r'^credits/$', 'myrobogals.rgmain.views.credits'),
	(r'^support/$', 'myrobogals.rgmain.views.support'),

	# Chapter-based newsletter API
	(r'^newsletter/(?P<chapterurl>.+)/subscribe/$', 'myrobogals.rgprofile.views.newslettersub'),
	(r'^newsletter/(?P<chapterurl>.+)/subscribe/done/$', 'myrobogals.rgprofile.views.newslettersubdone'),
	(r'^newsletter/(?P<chapterurl>.+)/unsubscribe/$', 'myrobogals.rgprofile.views.newsletterunsub'),
	(r'^newsletter/(?P<chapterurl>.+)/unsubscribe/done/$', 'myrobogals.rgprofile.views.newsletterunsubdone'),
	# Careers newsletter API
	(r'^api/newslettercareers/$', 'myrobogals.rgmessages.views.careersapi'),
	# Amplifier newsletter API
	(r'^api/newsletter/$', 'myrobogals.rgmessages.views.api'),
	# SMSGlobal delivery receipts API
	(r'^api/dlr/$', 'myrobogals.rgmessages.views.dlrapi'),
	# Google Maps KML API
	(r'^api/chapter-map.kml', 'myrobogals.rgchapter.views.chaptermap'),
	# Delete user API
	(r'^delete/user/(?P<userpk>\d+)/$', 'myrobogals.rgprofile.views.deleteuser'),

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
handler500 = 'myrobogals.rgmain.views.servererror'
