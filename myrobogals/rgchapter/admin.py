from myrobogals.rgchapter.models import DisplayColumn, ShirtSize, Award, AwardRecipient
from myrobogals import admin

class DisplayColumnAdmin(admin.ModelAdmin):
	list_display = ('field_name', 'display_name_en', 'display_name_de', 'order')

class ShirtSizeAdmin(admin.ModelAdmin):
	list_display = ('size_short', 'size_long', 'chapter', 'order')

class AwardAdmin(admin.ModelAdmin):
	list_display = ('award_name', 'award_type', 'award_description')
	
class AwardRecipientAdmin(admin.ModelAdmin):
	list_display = ('award', 'chapter', 'year', 'region', 'description')
	
admin.site.register(DisplayColumn, DisplayColumnAdmin)
admin.site.register(ShirtSize, ShirtSizeAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(AwardRecipient, AwardRecipientAdmin)
