from __future__ import unicode_literals
from future.builtins import *
import six


from django import forms

from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from myrg_users.models import RobogalsUser
from django.contrib.admin import widgets, helpers

from .models import RoleClass, Role

class RoleCreationForm(forms.ModelForm):
    class Meta:
        model = Role

    def clean_group(self):
        group = self.cleaned_data['group']
        applGroups = self.cleaned_data['role_class'].get_applicable_groups()
        if group in applGroups:
            return group
        else:
            raise forms.ValidationError(str(group) +
                " is not applicable. Applicable Groups are: " +
                ', '.join([str(x) for x in applGroups]))

    def save(self, commit=True):
        role = super(RoleCreationForm, self).save(commit=False)
        if commit:
            role.save()
        return role

class RoleChangeForm(forms.ModelForm):
    class Meta:
        model = Role

    def clean_group(self):
        group = self.cleaned_data['group']
        applGroups = self.cleaned_data['role_class'].get_applicable_groups()
        if group in applGroups:
            return group
        else:
            raise forms.ValidationError(str(group) +
                " is not applicable. Applicable Groups are: " +
                ', '.join([str(x) for x in applGroups]))
