"""
    myRobogals
    myrg_users/admin.py
    Custom RobogalsUser admin management

    2014
    Robogals Software Team
"""

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.utils.translation import ugettext_lazy as _

from .models import RobogalsUser
from .forms import RobogalsUserChangeForm, RobogalsUserCreationForm

# Based upon:
# * https://docs.djangoproject.com/en/1.6/topics/auth/customizing/#substituting-a-custom-user-model
# * http://www.caktusgroup.com/blog/2013/08/07/migrating-custom-user-model-django/
# * https://github.com/jonathanchu/django-custom-user-example/blob/master/customuser/accounts/admin.py
# * https://github.com/django/django/blob/master/django/contrib/auth/admin.py

class RobogalsUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = RobogalsUserChangeForm
    add_form = RobogalsUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
                    'username',
                    'primary_email',
                    'family_name',
                    'given_name',
                    'mobile',
                   )
    list_filter = (
                    'is_active',
                    'is_superuser',
                  )
    fieldsets = (
        (None, {'fields': (
                            'username',
                            'password'
                           )
               }
        ),
        (_('Personal info'), {'fields': (
                                            'family_name',
                                            'given_name',
                                            'preferred_name',
                                            'dob',
                                            'gender',
                                        )
                             }
        ),
        (_('Contact info'), {'fields': (
                                        'primary_email',
                                        'secondary_email',
                                        'mobile',
                                        #'country',
                                        'postcode',
                                       )
                            }
        ),
        (_('Personalisation'), {'fields': (
                                            #'subscriptions',
                                            #'biography',
                                            #'photo',
                                            'preferred_language',
                                          )
                               }
        ),
        (_('Privacy'), {'fields': (
                                    'profile_visibility',
                                    'primary_email_visibility',
                                    #'secondary_email_visibility',
                                    'dob_visibility',
                                   )
                       }
        ),
        (_('Internal info'), {'fields': (
                                            'is_active',
                                            'is_superuser',
                                            'groups',
                                            'user_permissions',
                                            'date_joined',
                                            'last_login',
                                        )
                              }
        ),
    )
    
    # These are required for the two-stage user add form.
    # They must include ALL required fields as minimum.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                        'username',
                        'family_name',
                        'given_name',
                        'primary_email',
                        'password1',
                        'password2',
                      )
               }
        ),
    )
    search_fields = ('username','primary_email','family_name','given_name','preferred_name')
    ordering = ('username','primary_email','family_name','given_name')
    filter_horizontal = ()

# Now register the new RobogalsUserAdmin...
admin.site.register(RobogalsUser, RobogalsUserAdmin)
