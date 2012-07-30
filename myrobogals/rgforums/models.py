from pytz import timezone, utc
from django.db import models
from django.utils.translation import ugettext_lazy as _
from myrobogals.auth.models import Group, User

class Category(models.Model):
	name = models.CharField('Name', max_length=80)
	chapter = models.ForeignKey(Group, null=True)
	exec_only = models.BooleanField(default=False)
	created_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')
		ordering = ['created_on']

	def __unicode__(self):
		return self.name

	def get_full_name(self):
		if self.chapter:
			visibility = _('%s') % (self.chapter.name)
		else:
			visibility = _('Global')
		if self.exec_only:
			availability = _('Executive only')
		else:
			availability = _('Open to Public')
		return _('%s (%s, %s)') % (self.name, visibility, availability)

class Forum(models.Model):
	name = models.CharField('Name', max_length=80)
	description = models.TextField(default = '')
	category = models.ForeignKey(Category, null=False)
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='forum_created_by')
	num_topics = models.IntegerField(default = 0)
	num_posts = models.IntegerField(default = 0)
	last_post_time = models.DateTimeField(blank=True, null=True)
	last_post_user = models.ForeignKey(User, null=True, related_name='forum_last_post_user')

	class Meta:
		verbose_name = "Forum"
		verbose_name_plural = "Forums"
		ordering = ['created_on']

	def __unicode__(self):
		return self.name

	def tz_obj(self):
		if self.category.chapter:
			return self.category.chapter.timezone.tz_obj()
		else:
			return timezone('UTC')

	def last_post_local(self):
		if self.last_post_time:
			if self.tz_obj() == utc:
				return self.last_post_time
			else:
				return self.tz_obj().fromutc(self.last_post_time)
		else:
			return None

	def created_on_local(self):
		if self.created_on:
			if self.tz_obj() == utc:
				return self.created_on
			else:
				return self.tz_obj().fromutc(self.created_on)
		else:
			return None

class Topic(models.Model):
	forum = models.ForeignKey(Forum)
	posted_by = models.ForeignKey(User, related_name='topic_posted_by')
	subject = models.CharField(max_length=80)
	num_views = models.IntegerField(default=0)
	num_replies = models.PositiveSmallIntegerField(default=0)
	created_on = models.DateTimeField(auto_now_add=True)
	last_post_time = models.DateTimeField(blank=True, null=True)
	last_post_user = models.ForeignKey(User, null=True, related_name='topic_last_post_user')
	sticky = models.BooleanField(default=False)

	class Meta:
		verbose_name = "Topic"
		verbose_name_plural = "Topics"
		ordering = ['-sticky', 'created_on']

	def __unicode__(self):
		return self.subject

	def tz_obj(self):
		if self.forum.category.chapter:
			return self.forum.category.chapter.timezone.tz_obj()
		else:
			return timezone('UTC')

	def last_post_local(self):
		if self.last_post_time:
			if self.tz_obj() == utc:
				return self.last_post_time
			else:
				return self.tz_obj().fromutc(self.last_post_time)
		else:
			return None

	def created_on_local(self):
		if self.created_on:
			if self.tz_obj() == utc:
				return self.created_on
			else:
				return self.tz_obj().fromutc(self.created_on)
		else:
			return None

class Post(models.Model):
	topic = models.ForeignKey(Topic)
	posted_by = models.ForeignKey(User, related_name='post_posted_by')
	message = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(blank=True, null=True)
	edited_by = models.ForeignKey(User, null=True, related_name='post_edited_by')

	class Meta:
		verbose_name = "Post"
		verbose_name_plural = "Posts"
		ordering = ['created_on']

	def __unicode__(self):
		return str(self.pk)

	def get_quote(self):
		msg = '>>' + self.posted_by.get_full_name() + ' wrote:\n' + self.message
		msg = msg.replace('\n', '\n>>')
		msg = msg + '\n'
		return msg

	def tz_obj(self):
		if self.topic.forum.category.chapter:
			return self.topic.forum.category.chapter.timezone.tz_obj()
		else:
			return timezone('UTC')

	def created_on_local(self):
		if self.created_on:
			if self.tz_obj() == utc:
				return self.created_on
			else:
				return self.tz_obj().fromutc(self.created_on)
		else:
			return None

	def updated_on_local(self):
		if self.updated_on:
			if self.tz_obj() == utc:
				return self.updated_on
			else:
				return self.tz_obj().fromutc(self.updated_on)
		else:
			return None
