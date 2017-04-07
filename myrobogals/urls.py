from django.conf.urls import url, include, i18n
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.static import serve as static_serve_view

from myrobogals import settings

from myrobogals.rgchapter import views as rgchapter_views
from myrobogals.rgconf import views as rgconf_views
from myrobogals.rgforums import views as rgforums_views
from myrobogals.rgmain import views as rgmain_views
from myrobogals.rgmessages import views as rgmessages_views
from myrobogals.rgprofile import views as rgprofile_views
from myrobogals.rgteaching import views as rgteaching_views
from myrobogals.rgweb import views as rgweb_views

from tinymce import urls as tinymce_urls

urlpatterns = [
	# Home
	url(r'^$', rgmain_views.home),

	# User functions
	url(r'^login/$', rgprofile_views.show_login),
	url(r'^login/process/$', rgprofile_views.process_login),
	url(r'^logout/$', auth_views.logout, {'next_page': '/'}),
	url(r'^chpass/$', auth_views.password_change, {'template_name': 'password_change_form.html', 'post_change_redirect': '/profile'}),
	url(r'^forgotpass/done/$', auth_views.password_reset_done, {'template_name': 'password_reset_done.html'}, name='password_reset_done'),
	url(r'^forgotpass/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', auth_views.password_reset_confirm, {'template_name': 'password_reset_confirm.html'}),
	url(r'^forgotpass/complete/$', auth_views.password_reset_complete, {'template_name': 'password_reset_complete.html'}, name='password_reset_complete'),
	url(r'^forgotpass/$', auth_views.password_reset, {'template_name': 'password_reset_form.html', 'email_template_name': 'password_reset_email.html'}),
	#url(r'^unsubscribe/(?P<uidb36>.+)/(?P<token>.+)/(?P<step>\d)/$', auth_views.unsubscribe),
	url(r'^join/$', rgchapter_views.joinlist),
	url(r'^join/(?P<chapterurl>.+)/$', rgprofile_views.joinchapter),
	url(r'^welcome/(?P<chapterurl>.+)/$', rgmain_views.welcome),

	# Profile menu
	url(r'^profile/$', rgprofile_views.redirtoself),
	url(r'^profile/contactdirectory/$', rgprofile_views.contactdirectory),
	url(r'^profile/edit/$', rgprofile_views.redirtoeditself),
	url(r'^profile/mobverify/$', rgprofile_views.mobverify),
	#url(r'^profile/(?P<username>.+)/edit/profileimage/$', 'profileimages.views.upload_profile_image'),
	url(r'^profile/(?P<username>.+)/edit/$', rgprofile_views.edituser),
	url(r'^profile/(?P<username>.+)/genpw/$', rgprofile_views.genpw),
	url(r'^profile/(?P<username>.+)/$', rgprofile_views.detail),
	
	# Chapters menu
	url(r'^chapters/$', rgchapter_views.list),
	url(r'^chapters/awards/$', rgchapter_views.awards),
	url(r'^chapters/awards/(?P<award_id>\d+)/$', rgchapter_views.awardsdesc),
	url(r'^chapters/my/$', rgchapter_views.redirtomy),
	url(r'^chapters/localtimes/$', rgchapter_views.localtimes),
	url(r'^chapters/(?P<chapterurl>.+)/lists/(?P<list_id>\d+)/edit/$', rgprofile_views.edituserlist),
	url(r'^chapters/(?P<chapterurl>.+)/lists/(?P<list_id>\d+)/$', rgprofile_views.viewlist),
	url(r'^chapters/(?P<chapterurl>.+)/lists/add/$', rgprofile_views.adduserlist),
	url(r'^chapters/(?P<chapterurl>.+)/lists/$', rgprofile_views.listuserlists),
	url(r'^chapters/(?P<chapterurl>.+)/edit/users/import/help/unis/$', rgprofile_views.unilist),
	url(r'^chapters/(?P<chapterurl>.+)/edit/users/import/help/$', rgprofile_views.importusershelp),
	url(r'^chapters/(?P<chapterurl>.+)/edit/users/import/$', rgprofile_views.importusers),
	url(r'^chapters/(?P<chapterurl>.+)/edit/users/export/$', rgprofile_views.exportusers),
	url(r'^chapters/(?P<chapterurl>.+)/edit/users/add/$', rgprofile_views.adduser),
	url(r'^chapters/(?P<chapterurl>.+)/edit/users/$', rgprofile_views.editusers),
	url(r'^chapters/(?P<chapterurl>.+)/edit/execs/$', rgprofile_views.editexecs),
	url(r'^chapters/(?P<chapterurl>.+)/edit/status/$', rgprofile_views.editstatus),
	url(r'^chapters/(?P<chapterurl>.+)/edit/$', rgchapter_views.editchapter),
	url(r'^chapters/(?P<chapterurl>.+)/websitedetails/$', rgweb_views.websitedetails),
	url(r'^chapters/(?P<chapterurl>.+)/join/$', rgprofile_views.joinchapter),
	url(r'^chapters/(?P<chapterurl>.+)/$', rgchapter_views.detail),
	url(r'^conferences/$', rgconf_views.home),
	url(r'^conferences/(?P<conf_id>\d+)/$', rgconf_views.rsvplist),
	url(r'^conferences/(?P<conf_id>\d+)/nametags\.csv$', rgconf_views.nametagscsv),
	url(r'^conferences/(?P<conf_id>\d+)/email/$', rgconf_views.rsvpemail),
	url(r'^conferences/(?P<conf_id>\d+)/(?P<username>.+)/rsvp/$', rgconf_views.editrsvp),
	url(r'^conferences/(?P<conf_id>\d+)/(?P<username>.+)/invoice/$', rgconf_views.showinvoice),

	# Forums
	# url(r'^forums/newcategory/$', rgforums_views.newcategory),
	# url(r'^forums/newforum/$', rgforums_views.newforum),
	# url(r'^forums/stickytopic/$', rgforums_views.stickytopic),
	# url(r'^forums/setmaxuploadfilesize/$', rgforums_views.setmaxuploadfilesize),
	# url(r'^forums/category/delete/(?P<category_id>\d+)/$', rgforums_views.deletecategory),
	# url(r'^forums/forum/delete/(?P<forum_id>\d+)/$', rgforums_views.deleteforum),
	# url(r'^forums/topic/delete/(?P<topic_id>\d+)/$', rgforums_views.deletetopic),
	# url(r'^forums/post/delete/(?P<post_id>\d+)/$', rgforums_views.deletepost),
	# url(r'^forums/post/fileoffenses/(?P<post_id>\d+)/$', rgforums_views.fileoffenses),
	# url(r'^forums/showforumoffenses/(?P<forum_id>\d+)/$', rgforums_views.showforumoffenses),
	# url(r'^forums/unwatchforum/(?P<forum_id>\d+)/$', rgforums_views.unwatchforum),
	# url(r'^forums/watchforum/(?P<forum_id>\d+)/$', rgforums_views.watchforum),
	# url(r'^forums/unwatchtopic/(?P<topic_id>\d+)/$', rgforums_views.unwatchtopic),
	# url(r'^forums/watchtopic/(?P<topic_id>\d+)/$', rgforums_views.watchtopic),
	# url(r'^forums/unwatchalltopics/$', rgforums_views.unwatchalltopics),
	# url(r'^forums/watchmytopics/$', rgforums_views.watchtopicwithmyposts),
	# url(r'^forums/unwatchall/(?P<uidb36>.+)/(?P<token>.+)/(?P<step>\d)/$', rgforums_views.unwatchall),
	# url(r'^forums/search/(?P<chapterurl>.+)/$', rgforums_views.search),
	# url(r'^forums/newtopic/(?P<forum_id>\d+)/$', rgforums_views.newtopic),
	# url(r'^forums/newpost/(?P<topic_id>\d+)/$', rgforums_views.newpost),
	# url(r'^forums/editpost/(?P<post_id>\d+)/$', rgforums_views.editpost),
	# url(r'^forums/upvote/(?P<post_id>\d+)/$', rgforums_views.topicupvote),
	# url(r'^forums/undoupvote/(?P<post_id>\d+)/$', rgforums_views.topicundoupvote),
	# url(r'^forums/deletefile/(?P<post_id>\d+)/(?P<file_id>\d+)/$', rgforums_views.deletefile),
	# url(r'^forums/downloadpostfile/(?P<post_id>\d+)/(?P<file_id>\d+)/$', rgforums_views.downloadpostfile),
	# url(r'^forums/editforum/(?P<forum_id>\d+)/$', rgforums_views.editforum),
	# url(r'^forums/topic/(?P<topic_id>\d+)/$', rgforums_views.viewtopic),
	# url(r'^forums/forum/(?P<forum_id>\d+)/$', rgforums_views.viewforum),
	# url(r'^forums/$', rgforums_views.forums),
	# url(r'^forums/(?P<forum_id>\d+)/blacklistuser/(?P<user_id>\d+)/$', rgforums_views.blacklistuser),
	# url(r'^forums/(?P<forum_id>\d+)/unblacklistuser/(?P<user_id>\d+)/$', rgforums_views.unblacklistuser'),

	# Workshops menu
	url(r'^teaching/$', rgteaching_views.teachhome),
	#url(r'^teaching/availability/$', rgteaching_views.availability),
	#url(r'^teaching/training/$', rgteaching_views.training),
	url(r'^teaching/list/$', rgteaching_views.listvisits),
	url(r'^teaching/printlist/$', rgteaching_views.printlistvisits),
	url(r'^teaching/statshelp/$', rgteaching_views.statshelp),
	url(r'^teaching/(?P<visit_id>\d+)/$', rgteaching_views.viewvisit),
	url(r'^teaching/(?P<visit_id>\d+)/deletemessage/(?P<message_id>\d+)/$', rgteaching_views.deletemessage),
	url(r'^teaching/(?P<visit_id>\d+)/invite/$', rgteaching_views.invitetovisit),
	url(r'^teaching/(?P<visit_id>\d+)/email/$', rgteaching_views.emailvisitattendees),
	url(r'^teaching/(?P<visit_id>\d+)/edit/$', rgteaching_views.editvisit),
	url(r'^teaching/(?P<visit_id>\d+)/stats/$', rgteaching_views.stats),
	url(r'^teaching/(?P<visit_id>\d+)/statsHoursPerPerson/$', rgteaching_views.statsHoursPerPerson),
	url(r'^teaching/(?P<visit_id>\d+)/cancel/$', rgteaching_views.cancelvisit),
	url(r'^teaching/(?P<visit_id>\d+)/reopen/$', rgteaching_views.reopenvisit),
	url(r'^teaching/(?P<event_id>\d+)/rsvp/(?P<user_id>\d+)/(?P<rsvp_type>.+)/$', rgteaching_views.rsvp),
	url(r'^teaching/schools/$', rgteaching_views.listschools),
	url(r'^teaching/unstarschool/$', rgteaching_views.unstarschool),
	url(r'^teaching/starschool/$', rgteaching_views.starschool),
	url(r'^teaching/copyschooldir/$', rgteaching_views.copyschool),
	url(r'^teaching/filllatlngschdir/$', rgteaching_views.filllatlngschdir),
	url(r'^teaching/schoolsdirectory/(?P<chapterurl>.+)/$', rgteaching_views.schoolsdirectory),
	url(r'^teaching/schools/(?P<school_id>\d+)/$', rgteaching_views.editschool),
	url(r'^teaching/schools/(?P<school_id>\d+)/delete/$', rgteaching_views.deleteschool),
	url(r'^teaching/schools/new/$', rgteaching_views.newschool),
	url(r'^teaching/(?P<school_id>\d+)/newvisit/$', rgteaching_views.newvisitwithschool),
	url(r'^teaching/new/$', rgteaching_views.newvisit),
	url(r'^reports/$', rgteaching_views.report_standard),
	url(r'^globalreports/$', rgteaching_views.report_global),
	url(r'^globalreports/breakdown/(?P<chaptershorten>.+)/$', rgteaching_views.report_global_breakdown),
	url(r'^progress/$', rgchapter_views.progresschapter),

	# Email & SMS menu
	url(r'^messages/img/(?P<msgid>\d+)/(?P<filename>.+)$', rgmessages_views.serveimg),
	url(r'^messages/(?P<msgid>\d+)/(?P<issue>.+)/$', rgmessages_views.servenewsletter),
	url(r'^messages/sms/write/$', rgmessages_views.writesms),
	url(r'^messages/sms/done/$', rgmessages_views.smsdone),
	url(r'^messages/sms/overlimit/$', rgmessages_views.smsoverlimit),
	url(r'^messages/email/write/$', rgmessages_views.writeemail),
	url(r'^messages/setmaxuploadfilesize/$', rgmessages_views.setmaxuploadfilesize),
	url(r'^messages/email/done/$', rgmessages_views.emaildone),
	url(r'^messages/newsletters/(?P<newsletter_id>\d+)/$', rgmessages_views.newslettercp),
	url(r'^messages/newsletters/(?P<newsletter_id>\d+)/import/$', rgmessages_views.importsubscribers),
	url(r'^messages/newsletters/(?P<newsletter_id>\d+)/import/help/$', rgmessages_views.importsubscribershelp),
	url(r'^messages/emailrecipients/(?P<email_id>\d+)/$', rgmessages_views.emailrecipients),
	url(r'^messages/smsrecipients/(?P<sms_id>\d+)/$', rgmessages_views.smsrecipients),
	url(r'^messages/showemail/(?P<email_id>\d+)/$', rgmessages_views.showemail),
	url(r'^messages/downloademailfile/(?P<email_id>\d+)/(?P<file_name>.+)/$', rgmessages_views.downloademailfile),
	url(r'^messages/history/$', rgmessages_views.msghistory),
	url(r'^messages/previewemail/$', rgmessages_views.previewemail),
	
	# Changelogs
	url(r'^changelogs/$', rgmain_views.changelogs),

	# Wiki
	url(r'^wiki/$', rgmain_views.wiki),

	# Static pages
	url(r'^credits/$', rgmain_views.credits),
	url(r'^support/$', rgmain_views.support),

	# Careers newsletter API
	url(r'^api/newslettercareers/$', rgmessages_views.careersapi),
	# Amplifier newsletter API
	url(r'^api/newsletter/$', rgmessages_views.api),
	# SMSGlobal delivery receipts API
	url(r'^api/dlr/$', rgmessages_views.dlrapi),
	# Google Maps KML API
	url(r'^api/chapter-map.kml', rgchapter_views.chaptermap),
	# Delete user API
	url(r'^delete/user/(?P<userpk>\d+)/$', rgprofile_views.deleteuser),

	# i18n helpers
	url(r'^i18n/', include(i18n)),
	# TinyMCE helpers
	url(r'^tinymce/', include(tinymce_urls)),
	
	# Admin site
	url(r'^topsecretarea/', include(admin.site.urls)),
]

# If running the local development server - this will serve the media files through it too
if settings.DEBUG:
	urlpatterns.append(url(r'^rgmedia/(?P<path>.*)$', static_serve_view, {'document_root': settings.MEDIA_ROOT,}))

# Custom view for 500 Internal Server Error
handler500 = 'myrobogals.rgmain.views.servererror'
