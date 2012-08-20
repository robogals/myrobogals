'''
This file uses code from LBForum, licensed under the BSD license.

Copyright (c) 2011, LBForum
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or other
materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
OF SUCH DAMAGE.
'''

from pytz import timezone, utc
from django.db import models
from django.utils.translation import ugettext_lazy as _
from myrobogals.auth.models import Group, User

class Category(models.Model):
	name = models.CharField('Name', max_length=80)
	chapter = models.ForeignKey(Group, blank=True, null=True)
	exec_only = models.BooleanField("For executives only", default=False)
	created_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')
		ordering = ['created_on']

	def __unicode__(self):
		return self.get_full_name()

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
	category = models.ForeignKey(Category)
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='forum_created_by')
	last_post_time = models.DateTimeField(blank=True, null=True)
	last_post_user = models.ForeignKey(User, blank=True, null=True, related_name='forum_last_post_user')

	class Meta:
		verbose_name = "Forum"
		verbose_name_plural = "Forums"
		ordering = ['created_on']

	def __unicode__(self):
		return self.name + ' [' + self.category.get_full_name() + ']'

	def number_of_topics(self):
		return Topic.objects.filter(forum=self).count()

	def number_of_posts(self):
		return Post.objects.filter(topic__forum=self).count()

class Topic(models.Model):
	forum = models.ForeignKey(Forum)
	posted_by = models.ForeignKey(User, related_name='topic_posted_by')
	subject = models.CharField(max_length=80)
	num_views = models.IntegerField("Number of views", default=0)
	created_on = models.DateTimeField(auto_now_add=True)
	last_post_time = models.DateTimeField(blank=True, null=True)
	last_post_user = models.ForeignKey(User, blank=True, null=True, related_name='topic_last_post_user')
	sticky = models.BooleanField("Set sticky", default=False)

	class Meta:
		verbose_name = "Topic"
		verbose_name_plural = "Topics"
		ordering = ['-sticky', 'created_on']

	def __unicode__(self):
		return self.subject + ' {' + self.forum.__unicode__() + '}'

	def number_of_replies(self):
		num_post = Post.objects.filter(topic=self).count()
		if num_post >= 1:
			return num_post - 1
		else:
			return 0

class Post(models.Model):
	topic = models.ForeignKey(Topic)
	posted_by = models.ForeignKey(User, related_name='post_posted_by')
	message = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(blank=True, null=True)
	edited_by = models.ForeignKey(User, blank=True, null=True, related_name='post_edited_by')

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
