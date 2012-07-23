from django.db import models
from myrobogals.auth.models import Group, User

class Category(models.Model):
	name = models.CharField('Name', max_length=80)
	description = models.TextField(default = '')
	chapter = models.ForeignKey(Group, null=True)
	exec_only = models.BooleanField(default=False)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(blank=True, null=True)

	class Meta:
		verbose_name = 'Category'
		verbose_name_plural = 'Categories'
		ordering = ['created_on']

	def __unicode__(self):
		return self.name

	def get_full_name(self):
		if self.chapter:
			visibility = u'%s' % (self.chapter.name)
		else:
			visibility = u'Global'
		if self.exec_only:
			availability = u'Executive only'
		else:
			availability = u'Open to Public'
		return u'%s (%s, %s)' % (self.name, visibility, availability)

class Forum(models.Model):
	name = models.CharField('Name', max_length=80)
	description = models.TextField(default = '')
	category = models.ForeignKey(Category, null=False)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(blank=True, null=True)
	num_topics = models.IntegerField(default = 0)
	num_posts = models.IntegerField(default = 0)

	last_post = models.CharField(max_length = 255, blank = True)#pickle obj

	class Meta:
		verbose_name = "Forum"
		verbose_name_plural = "Forums"
		ordering = ['created_on']

	def __unicode__(self):
		return self.name

class Topic(models.Model):
	forum = models.ForeignKey(Forum)
	posted_by = models.ForeignKey(User)
	subject = models.CharField(max_length=64)
	num_views = models.IntegerField(default=0)
	num_replies = models.PositiveSmallIntegerField(default=0)#posts...
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(blank=True, null=True)
	last_reply_on = models.DateTimeField(auto_now_add=True)
	last_post = models.CharField(max_length=255, blank=True)#pickle obj
	closed = models.BooleanField(default=False)

	class Meta:
		verbose_name = "Topic"
		verbose_name_plural = "Topics"
		ordering = ['created_on']

	def __unicode__(self):
		return self.subject

class Post(models.Model):
	topic = models.ForeignKey(Topic)
	posted_by = models.ForeignKey(User)
	message = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(blank=True, null=True)
	edited_by = models.CharField(max_length=255, blank=True)#user name

	class Meta:
		verbose_name = "Post"
		verbose_name_plural = "Posts"
		ordering = ['created_on']

	def __unicode__(self):
		return self.pk

	def get_quote(self):
		msg = '>>' + self.posted_by.get_full_name() + ' wrote:\n' + self.message
		msg = msg.replace('\n', '\n>>')
		msg = msg + '\n'
		return msg
