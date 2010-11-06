from myrobogals.auth.models import User
from myrobogals.rgprofile.models import PositionType, UserList
from myrobogals.rgprofile.usermodels import University, MobileRegexCollection, MobileRegex
from myrobogals import admin

class PositionTypeAdmin(admin.ModelAdmin):
	list_display = ('description', 'chapter', 'rank')
	search_fields = ('description', 'chapter', 'rank')

class UniversityAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)

class UserListAdmin(admin.ModelAdmin):
	list_display = ('name','chapter')
	search_fields = ('name',)
	filter_horizontal = ('users',)

class MobileRegexInline(admin.TabularInline):
	model = MobileRegex
	extra = 5

class MobileRegexCollectionAdmin(admin.ModelAdmin):
	inlines = [MobileRegexInline]

admin.site.register(MobileRegexCollection, MobileRegexCollectionAdmin)
admin.site.register(PositionType, PositionTypeAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(UserList, UserListAdmin)
