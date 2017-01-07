from myrobogals.rgprofile.models import User, PositionType, UserList, MemberStatus, Position, MemberStatusType
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BuiltinUserAdmin

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm

class PositionTypeAdmin(admin.ModelAdmin):
	list_display = ('description', 'chapter', 'rank')
	search_fields = ('description',)

class UserListAdmin(admin.ModelAdmin):
	list_display = ('name','chapter')
	search_fields = ('name',)
	filter_horizontal = ('users',)

class MemberStatusAdmin(admin.TabularInline):
	model = MemberStatus
	extra = 2

class PositionAdmin(admin.TabularInline):
	model = Position
	extra = 2

class UserAdmin(BuiltinUserAdmin):
	fieldsets = BuiltinUserAdmin.fieldsets + (
		('Basic info', {'fields': ('alt_email', 'dob', 'gender', 'photo', 'tshirt', 'trained', 'security_check', 'name_display')}),
		('Chapter', {'fields': ('chapter',)}),
		('University info (student members only)', {'fields': ('course', 'uni_start', 'uni_end', 'university', 'course_type', 'student_type', 'student_number', 'union_member')}),
		('Work info (industry members only)', {'fields': ('job_title', 'company')}),
		('Mobile info', {'fields': ('mobile', 'mobile_verified',)}),
		#('Photo'), {'fields': ('photo')}),
		('User preferences', {'fields': ('timezone','email_reminder_optin','email_chapter_optin', 'mobile_marketing_optin', 'mobile_reminder_optin', 'email_newsletter_optin', 'email_othernewsletter_optin', 'email_careers_newsletter_AU_optin')}),
		('Privacy settings', {'fields': ('privacy', 'dob_public', 'email_public')}),
		('Bio', {'fields': ('bio',)}),
		('Internal notes', {'fields': ('internal_notes',)}),
		('Aliases', {'fields': ('aliases',)}),
	)
	
	list_display = ('username', 'first_name', 'last_name', 'email', 'mobile', 'chapter', 'is_staff', 'is_active')
	list_filter = ('is_staff', 'is_superuser', 'is_active', 'chapter')
	search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')
	ordering = ('username',)
	inlines = (MemberStatusAdmin, PositionAdmin)
	filter_horizontal = ('aliases',)

	# The admin section add user form doesn't work, so lets just redirect people to our own that does!
	#def add_view(self, request):
	#	return HttpResponseRedirect('/chapters/global/edit/users/add/?return=/topsecretarea/auth/user/')

class MemberStatusTypeAdmin(admin.ModelAdmin):
	list_display = ('description', 'chapter')
	search_fields = ('description', 'chapter')

admin.site.register(User, UserAdmin)
admin.site.register(MemberStatusType, MemberStatusTypeAdmin)
admin.site.register(PositionType, PositionTypeAdmin)
admin.site.register(UserList, UserListAdmin)
