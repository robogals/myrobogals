from myrobogals.rgweb.models import Website
from django.contrib import admin

class WebsiteAdmin(admin.ModelAdmin):
	list_display = ('site_name', 'site_url', 'joomla_pass')
	search_fields = ('site_name', 'site_url', 'joomla_pass')

admin.site.register(Website, WebsiteAdmin)
