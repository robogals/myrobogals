from myrobogals.rgchapter.models import DisplayColumn, ShirtSize
from myrobogals import admin

class DisplayColumnAdmin(admin.ModelAdmin):
	list_display = ('field_name', 'display_name_en', 'display_name_de', 'order')

class ShirtSizeAdmin(admin.ModelAdmin):
	list_display = ('size_short', 'size_long', 'chapter', 'order')

admin.site.register(DisplayColumn, DisplayColumnAdmin)
admin.site.register(ShirtSize, ShirtSizeAdmin)
