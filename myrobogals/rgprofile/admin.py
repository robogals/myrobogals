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

# TODO: fix this so it actually works. Then we don't need to redirect
# outside of the admin panel to get a working "add user" form.
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class UserAdmin(BuiltinUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm
	
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
	list_display = ('description', 'chapter', 'type_of_person')
	search_fields = ('description', 'chapter')

admin.site.register(User, UserAdmin)
admin.site.register(MemberStatusType, MemberStatusTypeAdmin)
admin.site.register(PositionType, PositionTypeAdmin)
admin.site.register(UserList, UserListAdmin)
