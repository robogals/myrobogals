from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.utils.translation import ugettext_lazy as _

from .models import RobogalsUser

# Based upon:
# * https://docs.djangoproject.com/en/1.6/topics/auth/customizing/#substituting-a-custom-user-model
# * http://www.caktusgroup.com/blog/2013/08/07/migrating-custom-user-model-django/
# * https://github.com/jonathanchu/django-custom-user-example/blob/master/customuser/accounts/forms.py
# * https://github.com/django/django/blob/master/django/contrib/auth/forms.py

class RobogalsUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = RobogalsUser
        fields = (
                    'username',
                    'primary_email',
                  )
                  
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RobogalsUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class RobogalsUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=_('Password'),
                                         help_text= ("Raw passwords are not stored, so there is no way to see this user's password, but you can change the password using <a href='password/'>this form</a>."))

    class Meta:
        model = RobogalsUser

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']

