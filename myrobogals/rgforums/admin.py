from myrobogals.rgforums.models import Category, Forum, Topic, Post
from django.contrib import admin

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'chapter', 'created_on')
	readonly_fields = ('created_on',)
	fieldsets = (
		(None, {'fields': ('name', 'chapter', 'exec_only', 'created_on')}),
	)

class ForumAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'category', 'created_on', 'created_by')
	readonly_fields = ('created_on',)
	fieldsets = (
		(None, {'fields': ('name', 'description', 'category')}),
		('Creator', {'fields': ('created_by', 'created_on')}),
		('Last post info', {'fields': ('last_post_user', 'last_post_time')}),
	)

class TopicAdmin(admin.ModelAdmin):
	list_display = ('subject', 'forum', 'created_on', 'posted_by')
	readonly_fields = ('created_on',)
	fieldsets = (
		(None, {'fields': ('subject', 'forum', 'posted_by', 'created_on', 'sticky')}),
		('Last post info', {'fields': ('last_post_user', 'last_post_time')}),
	)

class PostAdmin(admin.ModelAdmin):
	list_display = ('message', 'topic', 'posted_by')
	readonly_fields = ('created_on',)
	fieldsets = (
		(None, {'fields': ('topic', 'posted_by', 'message', 'created_on')}),
		('Last edit info', {'fields': ('edited_by', 'updated_on')}),
	)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
