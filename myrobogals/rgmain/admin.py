from myrobogals.rgmain.models import University
from django.contrib import admin

class UniversityAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)

admin.site.register(University, UniversityAdmin)
