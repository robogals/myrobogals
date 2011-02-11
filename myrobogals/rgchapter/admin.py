from myrobogals.rgchapter.models import DisplayColumn
from myrobogals import admin

class DisplayColumnAdmin(admin.ModelAdmin):
	list_display = ('field_name', 'display_name_en', 'display_name_de', 'order')

admin.site.register(DisplayColumn, DisplayColumnAdmin)
