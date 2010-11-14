from django import template
from django.conf import settings
from myrobogals import admin
from myrobogals.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
from myrobogals.auth.models import EmailDomain, User, Group, MemberStatus, MemberStatusType
from myrobogals.rgprofile.models import Position
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.html import escape


class GroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    #filter_horizontal = ('permissions',)
    fieldsets = (
        (None, {'fields': ('name', 'short', 'myrobogals_url', 'status', 'creation_date', 'university', 'location', 'parent', 'timezone', 'mobile_regexes', 'is_joinable')}),
        ('Address info', {'fields': ('address', 'city', 'state', 'postcode', 'country')}),
        ('Faculty contact', {'fields': ('faculty_contact', 'faculty_position', 'faculty_department', 'faculty_email', 'faculty_phone')}),
        ('Chapter-specific fields', {'fields': ('student_number_enable', 'student_number_required', 'student_number_label', 'student_union_enable', 'student_union_required', 'student_union_label')}),
        ('Default welcome email', {'fields': ('welcome_email_subject', 'welcome_email_msg', 'welcome_email_html')}),
        ('Default invite email', {'fields': ('invite_email_subject', 'invite_email_msg', 'invite_email_html')}),
        ('Custom pages', {'fields': ('welcome_page', 'join_page')}),
        ('Other', {'fields': ('infobox', 'website_url', 'facebook_url', 'emailtext', 'smstext', 'photo', 'default_email_domain')}),
        ('FTP details', {'fields': ('upload_exec_list', 'ftp_host', 'ftp_user', 'ftp_pass', 'ftp_path')}),
    )

class MemberStatusAdmin(admin.TabularInline):
	model = MemberStatus
	extra = 2

class PositionAdmin(admin.TabularInline):
	model = Position
	extra = 2

class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'alt_email', 'dob', 'gender', 'photo')}),
        ('Chapter', {'fields': ('groups',)}),
        ('University info (student members only)', {'fields': ('course', 'uni_start', 'uni_end', 'university', 'course_type', 'student_type', 'student_number', 'union_member')}),
        ('Work info (industry members only)', {'fields': ('job_title', 'company')}),
        ('Mobile info', {'fields': ('mobile', 'mobile_verified',)}),
        #('Photo'), {'fields': ('photo')}),
        ('User preferences', {'fields': ('timezone','email_reminder_optin','email_chapter_optin', 'mobile_marketing_optin', 'mobile_reminder_optin', 'email_newsletter_optin', 'email_othernewsletter_optin')}),
        ('Privacy settings', {'fields': ('privacy', 'dob_public', 'email_public')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Bio', {'fields': ('bio',)}),
        ('Internal notes', {'fields': ('internal_notes',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'first_name', 'last_name', 'email', 'mobile', 'chapter', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')
    ordering = ('username',)
    inlines = (MemberStatusAdmin, PositionAdmin)

    def __call__(self, request, url):
        # this should not be here, but must be due to the way __call__ routes
        # in ModelAdmin.
        if url is None:
            return self.changelist_view(request)
        if url.endswith('password'):
            return self.user_change_password(request, url.split('/')[0])
        return super(UserAdmin, self).__call__(request, url)
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns
        return patterns('',
            (r'^(\d+)/password/$', self.admin_site.admin_view(self.user_change_password))
        ) + super(UserAdmin, self).get_urls()

    def add_view(self, request):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404('Your user does not have the "Change user" permission. In order to add users, Django requires that your user account have both the "Add user" and "Change user" permissions set.')
            raise PermissionDenied
        if request.method == 'POST':
            form = self.add_form(request.POST)
            if form.is_valid():
                new_user = form.save()
                msg = 'The %(name)s "%(obj)s" was added successfully.' % {'name': 'user', 'obj': new_user}
                self.log_addition(request, new_user)
                if "_addanother" in request.POST:
                    request.user.message_set.create(message=msg)
                    return HttpResponseRedirect(request.path)
                elif '_popup' in request.REQUEST:
                    return self.response_add(request, new_user)
                else:
                    request.user.message_set.create(message=msg + ' ' + "You may edit it again below.")
                    return HttpResponseRedirect('../%s/' % new_user.id)
        else:
            form = self.add_form()
        return render_to_response('admin/auth/user/add_form.html', {
            'title': 'Add user',
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_add_permission': True,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_file_field': False,
            'has_absolute_url': False,
            'auto_populated_fields': (),
            'opts': self.model._meta,
            'save_as': False,
            'username_help_text': self.model._meta.get_field('username').help_text,
            'root_path': self.admin_site.root_path,
            'app_label': self.model._meta.app_label,            
        }, context_instance=template.RequestContext(request))

    def user_change_password(self, request, id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.model, pk=id)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                new_user = form.save()
                msg = 'Password changed successfully.'
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)
        return render_to_response('admin/auth/user/change_password.html', {
            'title': 'Change password: %s' % escape(user.username),
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))

class MemberStatusTypeAdmin(admin.ModelAdmin):
	list_display = ('description', 'chapter', 'type_of_person')
	search_fields = ('description', 'chapter')

admin.site.register(EmailDomain)
admin.site.register(Group, GroupAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(MemberStatusType, MemberStatusTypeAdmin)
