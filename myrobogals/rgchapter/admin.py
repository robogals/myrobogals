from myrobogals.rgchapter.models import DisplayColumn, ShirtSize, Award, AwardRecipient, Chapter
from django.contrib import admin

class DisplayColumnAdmin(admin.ModelAdmin):
	list_display = ('field_name', 'display_name_en', 'display_name_nl', 'display_name_ja', 'order')

class ShirtSizeAdmin(admin.ModelAdmin):
	list_display = ('size_short', 'size_long', 'chapter', 'order')

class AwardAdmin(admin.ModelAdmin):
	list_display = ('award_name', 'award_type', 'award_description')
	
class AwardRecipientAdmin(admin.ModelAdmin):
	list_display = ('award', 'chapter', 'year', 'region', 'description')

class ChapterAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    fieldsets = (
        (None, {'fields': ('name', 'short', 'short_en', 'myrobogals_url', 'status', 'creation_date', 'university', 'location', 'parent', 'timezone', 'mobile_regexes', 'is_joinable', 'exclude_in_reports', 'name_display', 'latitude', 'longitude')}),
        ('Annual goal', {'fields': ('goal', 'goal_start')}),
        ('Chapter-specific fields', {'fields': ('student_number_enable', 'student_number_required', 'student_number_label', 'student_union_enable', 'student_union_required', 'student_union_label', 'tshirt_enable', 'tshirt_required', 'tshirt_label', 'police_check_number_enable', 'police_check_number_required', 'police_check_number_label')}),
        ('Welcome email', {'fields': ('welcome_email_enable', 'welcome_email_subject', 'welcome_email_msg', 'welcome_email_html')}),
        ('Default invite email', {'fields': ('invite_email_subject', 'invite_email_msg', 'invite_email_html')}),
        ('Custom pages', {'fields': ('welcome_page', 'join_page')}),
        ('Address info', {'fields': ('address', 'city', 'state', 'postcode', 'country')}),
        ('Faculty contact', {'fields': ('faculty_contact', 'faculty_position', 'faculty_department', 'faculty_email', 'faculty_phone')}),
        ('Other', {'fields': ('infobox', 'website_url', 'facebook_url', 'emailtext', 'smstext', 'notify_enable', 'notify_list', 'photo', 'sms_limit', 'display_columns')}),
        ('FTP details', {'fields': ('upload_exec_list', 'ftp_host', 'ftp_user', 'ftp_pass', 'ftp_path')}),
    )
	
admin.site.register(DisplayColumn, DisplayColumnAdmin)
admin.site.register(ShirtSize, ShirtSizeAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(AwardRecipient, AwardRecipientAdmin)
admin.site.register(Chapter, ChapterAdmin)
