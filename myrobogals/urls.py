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
from myrobogals.rgteaching.views import quickentry, eventvisit, report
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
	# url(r'^forums/', include('myrobogals.rgforums.urls')),

	# Workshops menu
	url(r'^teaching/', include('myrobogals.rgteaching.urls')),

	url(r'^reports/$', report.report_standard),
	url(r'^globalreports/$', report.report_global),
	url(r'^globalreports/breakdown/(?P<chaptershorten>.+)/$', report.report_global_breakdown),
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
