from django.contrib import admin
from api_1_0.models import User, Profile


class UserInline(admin.StackedInline):
    model = Profile
    #extra = 5

class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['username']}),
        ('Detail information', {'fields': (['first_name'],
                              ['last_name'],
                              ['email'],
                              ['password'],
                              ['is_staff'],
                              ['is_active'],
                              ['is_superuser'],
                              #['last_login'],
                              #['date_joined'],
                              ['user_permissions']),
                              
                              'classes': ['collapse']}),
    ]
    inlines = [UserInline]
    
#class UserAdmin(admin.ModelAdmin):
    #exclude = (['last_login'],
     #          ['date_joined'],)
    
admin.site.register(User, UserAdmin)