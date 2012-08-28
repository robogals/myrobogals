import datetime
from tinymce.widgets import TinyMCE
from django import forms
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from myrobogals.auth.decorators import login_required
from myrobogals.auth.models import Group, User
from myrobogals.rgforums.models import Category, Forum, Topic, Post
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient

@login_required
def newcategory(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	if request.user.is_superuser:
		if 'category' in request.GET and 'visibility' in request.GET and 'availability' in request.GET:
			if request.GET['category']:
				newCategory = Category()
				newCategory.name = request.GET['category']
				if request.GET['visibility']:
					newCategory.chapter = Group.objects.get(pk=request.GET['visibility'])
				if request.GET['availability'] == 'public':
					newCategory.exec_only = False
				elif request.GET['availability'] == 'execonly':
					newCategory.exec_only = True
				else:
					raise Http404
				if Category.objects.filter(name=newCategory.name, chapter=newCategory.chapter, exec_only=newCategory.exec_only):
					msg = 'A similar category already exists'
					request.user.message_set.create(message=unicode(_(msg)))
				else:
					newCategory.save()
			else:
				msg = 'The field "Category name" can not be empty'
				request.user.message_set.create(message=unicode(_(msg)))
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			elif 'return' in request.POST:
				return HttpResponseRedirect(request.POST['return'])
			elif newCategory.chapter:
				return HttpResponseRedirect('/forums/' + newCategory.chapter.myrobogals_url + '/')
			else:
				return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
		else:
			raise Http404
	else:
		raise Http404

@login_required
def deletecategory(request, category_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	if request.user.is_superuser:
		c = get_object_or_404(Category, pk=category_id)
		chapter = c.chapter
		request.user.message_set.create(message=unicode(_('Category "' + c.name + '" deleted')))
		c.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif chapter:
			return HttpResponseRedirect('/forums/' + chapter.myrobogals_url + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def newforum(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	if 'forum' in request.GET and 'category' in request.GET and 'description' in request.GET:
		user = request.user
		g = get_object_or_404(Category, pk=request.GET['category'])
		c = g.chapter
		if (user.is_superuser) or (user.is_staff and (c == user.chapter)):
			if request.GET['forum'] and request.GET['description']:
				newForum = Forum()
				newForum.name = request.GET['forum']
				newForum.description = request.GET['description']
				newForum.category = g
				newForum.created_by = user
				if Forum.objects.filter(category=newForum.category, name=newForum.name):
					msg = 'A similar forum already exists'
					request.user.message_set.create(message=unicode(_(msg)))
				else:
					newForum.save()
			else:
				msg = 'The fields "Forum name" and "Description" can not be empty'
				request.user.message_set.create(message=unicode(_(msg)))
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			elif 'return' in request.POST:
				return HttpResponseRedirect(request.POST['return'])
			elif c:
				return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/')
			else:
				return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
		else:
			raise Http404
	else:
		raise Http404

@login_required
def editforum(request, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	edit = get_object_or_404(Forum, pk=forum_id)
	c = edit.category.chapter
	if ((not edit.category.chapter) and (not request.user.is_superuser)) or (edit.category.chapter and (((not request.user.is_staff) and (not request.user.is_superuser)) or ((c != request.user.chapter) and (not request.user.is_superuser)))):
		raise Http404
	if (request.method == 'POST'):
		if request.POST['forum'] and request.POST['description']:
			edit.name = request.POST['forum']
			edit.description = request.POST['description']
			edit.save()
		else:
			msg = 'The fields "new forum name" and "new description" can not be empty'
			request.user.message_set.create(message=unicode(_(msg)))
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def watchforum(request, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	user = request.user
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		f.watchers.add(user)
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def unwatchforum(request, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	user = request.user
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		f.watchers.remove(user)
		for topic in f.topic_set.all():
			topic.watchers.remove(user)
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def forums(request, chapterurl):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	editForum = ''
	globExecCategories = None
	globPubCategories = None
	localExecCategories = None
	localPubCategories = None
	if request.user.is_superuser or (request.user.is_staff and (c == request.user.chapter)):
		globExecCategories = Category.objects.filter(chapter__isnull=True, exec_only=True)
		globPubCategories = Category.objects.filter(chapter__isnull=True, exec_only=False)
		localExecCategories = Category.objects.filter(chapter=c, exec_only=True)
		localPubCategories = Category.objects.filter(chapter=c, exec_only=False)
	elif c == request.user.chapter:
		globPubCategories = Category.objects.filter(chapter__isnull=True, exec_only=False)
		localPubCategories = Category.objects.filter(chapter=c, exec_only=False)
	else:
		raise Http404
	if 'editForumId' in request.GET:
		edit = get_object_or_404(Forum, pk=request.GET['editForumId'])
		if ((not edit.category.chapter) and (not request.user.is_superuser)) or (edit.category.chapter and (((not request.user.is_staff) and (not request.user.is_superuser)) or ((c != request.user.chapter) and (not request.user.is_superuser)))):
			raise Http404
		editForum = edit.pk
	onlines = User.objects.filter(forum_last_act__gt=(datetime.datetime.now() - datetime.timedelta(hours=1)))
	online_users = []
	for o in onlines:
		if request.user.is_superuser:
			online_users.append((True, o))
		elif o.privacy >= 20:
			online_users.append((True, o))
		elif o.privacy >= 10:
			if not request.user.is_authenticated():
				online_users.append((False, o))
			else:
				online_users.append((True, o))
		elif o.privacy >= 5:
			if not request.user.is_authenticated():
				online_users.append((False, o))
			elif not (request.user.chapter == o.chapter):
				online_users.append((False, o))
			else:
				online_users.append((True, o))
		else:
			if not request.user.is_authenticated():
				online_users.append((False, o))
			elif not (request.user.chapter == o.chapter):
				online_users.append((False, o))
			elif not request.user.is_staff:
				online_users.append((False, o))
			else:
				online_users.append((True, o))
	num_online_users = len(online_users)
	total_num_topics = Topic.objects.count()
	total_num_posts = Post.objects.count()
	return render_to_response('forums.html', {'chapter': c, 'globExecCategories': globExecCategories, 'globPubCategories': globPubCategories, 'localExecCategories': localExecCategories, 'localPubCategories': localPubCategories, 'return': request.path, 'user': request.user, 'online_users': online_users, 'num_online_users': num_online_users, 'total_num_topics': total_num_topics, 'total_num_posts': total_num_posts, 'editForum': editForum}, context_instance=RequestContext(request))

class NewTopicForm(forms.Form):
	subject = forms.CharField(label=_('New Topic:'), max_length=80, widget=forms.TextInput(attrs={'size': '60'}))
	message = forms.CharField(label=_('Message:'), widget=TinyMCE(attrs={'cols': 50}))

@login_required
def newtopic(request, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	user = request.user
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		if request.method == 'POST':
			topicform = NewTopicForm(request.POST)
			if topicform.is_valid():
				data = topicform.cleaned_data
				newTopic = Topic()
				newTopic.forum = f
				newTopic.posted_by = user
				newTopic.subject = data['subject']
				newTopic.last_post_time = datetime.datetime.now()
				newTopic.last_post_user = user
				if Topic.objects.filter(forum=newTopic.forum, subject=newTopic.subject):
					msg = 'A similar topic already exists'
					request.user.message_set.create(message=unicode(_(msg)))
				else:
					newTopic.save()
					postMessage = Post()
					postMessage.topic = newTopic
					postMessage.posted_by = user
					postMessage.message = data['message']
					postMessage.save()
					f.last_post_time = datetime.datetime.now()
					f.last_post_user = user
					f.save()
					watchers = f.watchers.all().exclude(pk=request.user.pk)
					if watchers:
						message = EmailMessage()
						message.subject = 'New Topic: ' + newTopic.subject
						message.body = 'New topic for forum "' + f.name + '" in category "' + g.name +'"\n\nTopic subject: ' + newTopic.subject + ' (started by ' + newTopic.posted_by.get_full_name() + ')\n\nTopic Message:\n' + postMessage.message
						message.from_name = "myRobogals"
						message.from_address = "my@robogals.org"
						message.reply_address = "my@robogals.org"
						message.sender = User.objects.get(username='edit')
						message.html = False
						message.email_type = 1
						message.status = -1
						message.save()
						for watcher in watchers:
							recipient = EmailRecipient()
							recipient.message = message
							recipient.user = watcher
							recipient.to_name = watcher.get_full_name()
							recipient.to_address = watcher.email
							recipient.save()
						message.status = 0
						message.save()
			else:
				request.user.message_set.create(message=unicode(_('The fields "New Topic" and "Message" can not be empty')))
		else:
			raise Http404
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/forum/' + str(f.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/forum/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def stickytopic(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	if request.user.is_superuser and (request.method == 'POST'):
		t = None
		for topic_id in request.POST:
			topic = get_object_or_404(Topic, pk=topic_id)
			topic.sticky = False if topic.sticky else True
			topic.save()
			t = topic
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif t.forum.category.chapter:
			return HttpResponseRedirect('/forums/' + t.forum.category.chapter.myrobogals_url + '/forum/' + str(t.forum.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/forum/' + str(t.forum.pk) + '/')
	else:
		raise Http404

@login_required
def watchtopic(request, topic_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	t = get_object_or_404(Topic, pk=topic_id)
	f = t.forum
	g = f.category
	c = g.chapter
	user = request.user
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		if not f.watchers.filter(pk=user.pk):
			t.watchers.add(user)
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/forum/' + str(f.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/forum/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def watchtopicwithmyposts(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	posts = Post.objects.filter(posted_by=request.user)
	for post in posts:
		t = post.topic
		f = t.forum
		g = f.category
		c = g.chapter
		user = request.user
		if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
			if not f.watchers.filter(pk=user.pk):
				t.watchers.add(user)
	if 'return' in request.GET:
		return HttpResponseRedirect(request.GET['return'])
	elif 'return' in request.POST:
		return HttpResponseRedirect(request.POST['return'])
	elif c:
		return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/')
	else:
		return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')


@login_required
def unwatchtopic(request, topic_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	t = get_object_or_404(Topic, pk=topic_id)
	f = t.forum
	g = f.category
	c = g.chapter
	user = request.user
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		if f.watchers.filter(pk=user.pk):
			f.watchers.remove(user)
			for topic in f.topic_set.all():
				if topic != t:
					topic.watchers.add(user)
				else:
					topic.watchers.remove(user)
		else:
			t.watchers.remove(user)
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/forum/' + str(f.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/forum/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def deleteforum(request, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	if request.user.is_superuser:
		f = get_object_or_404(Forum, pk=forum_id)
		chapter = f.category.chapter
		request.user.message_set.create(message=unicode(_('Forum "' + f.name + '" deleted')))
		f.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif chapter:
			return HttpResponseRedirect('/forums/' + chapter.myrobogals_url + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def viewforum(request, chapterurl, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	chapterHome = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	if c and (c != chapterHome):
		raise Http404
	user = request.user
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		topicform = NewTopicForm(None)
		topics_list = f.topic_set.all()
		paginator = Paginator(topics_list, 10)
		page = request.GET.get('page')
		try:
			topics = paginator.page(page)
		except EmptyPage:
			topics = paginator.page(paginator.num_pages)
		except:
			topics = paginator.page(1)
		return render_to_response('forum_view.html', {'chapter': c, 'topics': topics, 'topicform': topicform, 'forum': f, 'chapterHome': chapterHome, 'returnLastPage': request.path + '?' + 'page=' + '-1', 'return': request.path + '?' + request.META['QUERY_STRING']}, context_instance=RequestContext(request))
	else:
		raise Http404

@login_required
def deletepost(request, post_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	p = get_object_or_404(Post, pk=post_id)
	t = p.topic
	f = t.forum
	g = f.category
	c = g.chapter
	if (user.is_superuser):
		p.delete()
		t.num_views = t.num_views - 1
		t.save()
		request.user.message_set.create(message=unicode(_('Post deleted')))
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/topic/' + str(t.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/topic/' + str(t.pk) + '/')
	else:
		raise Http404

class WritePostForm(forms.Form):
	message = forms.CharField(widget=TinyMCE(attrs={'cols': 65}))

@login_required
def editpost(request, post_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	p = get_object_or_404(Post, pk=post_id)
	t = p.topic
	f = t.forum
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (p.posted_by == user):
		if (request.method == 'POST'):
			postform = WritePostForm(request.POST)
			if postform.is_valid():
				data = postform.cleaned_data
				p.message = data['message']
				p.updated_on = datetime.datetime.now()
				p.edited_by = user
				p.save()
				t.num_views = t.num_views - 1
				t.save()
			else:
				request.user.message_set.create(message=unicode(_('The fields "Message" can not be empty')))
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			elif 'return' in request.POST:
				return HttpResponseRedirect(request.POST['return'])
			elif c:
				return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/topic/' + str(t.pk) + '/')
			else:
				return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/topic/' + str(t.pk) + '/')
		else:
			raise Http404
	else:
		raise Http404

@login_required
def newpost(request, topic_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	t = get_object_or_404(Topic, pk=topic_id)
	f = t.forum
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		if request.method == 'POST':
			postform = WritePostForm(request.POST)
			if postform.is_valid():
				data = postform.cleaned_data
				postMessage = Post()
				postMessage.topic = t
				postMessage.posted_by = user
				postMessage.message = data['message']
				postMessage.save()
				t.num_views = t.num_views - 1
				t.last_post_time = datetime.datetime.now()
				t.last_post_user = user
				t.save()
				f.last_post_time = datetime.datetime.now()
				f.last_post_user = user
				f.save()
				watchers = (f.watchers.all() | t.watchers.all()).distinct().exclude(pk=request.user.pk)
				if watchers:
					message = EmailMessage()
					message.subject = 'New Post for topic "' + t.subject + '"'
					message.body = 'New post for topic "' + t.subject + '" for forum "' + f.name + '" in category "' + g.name + '"\n\nPost message: (posted by ' + postMessage.posted_by.get_full_name() + ')\n' + postMessage.message
					message.from_name = "myRobogals"
					message.from_address = "my@robogals.org"
					message.reply_address = "my@robogals.org"
					message.sender = User.objects.get(pk=1692) #need to change
					message.html = False
					message.email_type = 1
					message.status = -1
					message.save()
					for watcher in watchers:
						recipient = EmailRecipient()
						recipient.message = message
						recipient.user = watcher
						recipient.to_name = watcher.get_full_name()
						recipient.to_address = watcher.email
						recipient.save()
					message.status = 0
					message.save()
			else:
				request.user.message_set.create(message=unicode(_('The fields "Message" can not be empty')))
		else:
			raise Http404
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/topic/' + str(t.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/topic/' + str(t.pk) + '/')
	else:
		raise Http404

@login_required
def deletetopic(request, topic_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	if request.user.is_superuser:
		t = get_object_or_404(Topic, pk=topic_id)
		f = t.forum
		chapter = f.category.chapter
		request.user.message_set.create(message=unicode(_('Topic "' + t.subject + '" deleted')))
		t.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		elif chapter:
			return HttpResponseRedirect('/forums/' + chapter.myrobogals_url + '/forum/' + str(f.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/forum/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def viewtopic(request, chapterurl, topic_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	chapterHome = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	user = request.user
	t = get_object_or_404(Topic, pk=topic_id)
	f = t.forum
	g = f.category
	c = g.chapter
	if c and (c != chapterHome):
		raise Http404
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		editPost = ''
		if ('quotePostId' in request.GET) and ('editPostId' not in request.GET):
			quote = Post.objects.get(pk=request.GET['quotePostId'])
			postform = WritePostForm({'message': quote.get_quote()})
		elif ('editPostId' in request.GET) and ('quotePostId' not in request.GET):
			edit = Post.objects.get(pk=request.GET['editPostId'])
			if (not request.user.is_superuser) and (edit.posted_by != request.user):
				raise Http404
			postform = WritePostForm({'message': edit.message})
			editPost = edit.pk
		else:
			postform = WritePostForm(None)
			t.num_views = t.num_views + 1
			t.save()
		posts_ls = t.post_set.all()
		posts_list = []
		for post in posts_ls:
			if request.user.is_superuser:
				posts_list.append((True, post, Post.objects.filter(posted_by = post.posted_by).count(), 'online' if (post.posted_by.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
			elif post.posted_by.privacy >= 20:
				posts_list.append((True, post, Post.objects.filter(posted_by = post.posted_by).count(), 'online' if (post.posted_by.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
			elif post.posted_by.privacy >= 10:
				if not request.user.is_authenticated():
					posts_list.append((False, post))
				else:
					posts_list.append((True, post, Post.objects.filter(posted_by = post.posted_by).count(), 'online' if (post.posted_by.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
			elif post.posted_by.privacy >= 5:
				if not request.user.is_authenticated():
					posts_list.append((False, post))
				elif not (request.user.chapter == post.posted_by.chapter):
					posts_list.append((False, post))
				else:
					posts_list.append((True, post, Post.objects.filter(posted_by = post.posted_by).count(), 'online' if (post.posted_by.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
			else:
				if not request.user.is_authenticated():
					posts_list.append((False, post))
				elif not (request.user.chapter == post.posted_by.chapter):
					posts_list.append((False, post))
				elif not request.user.is_staff:
					posts_list.append((False, post))
				else:
					posts_list.append((True, post, Post.objects.filter(posted_by = post.posted_by).count(), 'online' if (post.posted_by.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
		paginator = Paginator(posts_list, 10)
		page = request.GET.get('page')
		try:
			posts = paginator.page(page)
		except EmptyPage:
			posts = paginator.page(paginator.num_pages)
			page = paginator.num_pages
		except:
			posts = paginator.page(1)
			page = 1
		return render_to_response('topic_view.html', {'chapter': c, 'posts': posts, 'postform': postform, 'topic': t, 'chapterHome': chapterHome, 'forum': f, 'editPost': editPost, 'returnLastPage': request.path + '?' + 'page=' + '-1', 'return': request.path + '?' + 'page=' + str(page)}, context_instance=RequestContext(request))
	else:
		raise Http404

@login_required
def search(request, chapterurl):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	search = ''
	forums = None
	topics = None
	user = request.user
	if 'search' in request.GET:
		search = request.GET['search']
		if user.is_superuser:
			forums = Forum.objects.filter(Q(name__icontains=search)).order_by('category__chapter', '-category__exec_only', 'created_on')
			topics = Topic.objects.filter(Q(subject__icontains=search)).order_by('forum__category__chapter', '-forum__category__exec_only', 'created_on')
		elif user.is_staff:
			forums = Forum.objects.filter(Q(name__icontains=search) & (Q(category__chapter=user.chapter) | Q(category__chapter__isnull=True))).order_by('category__chapter', '-category__exec_only', 'created_on')
			topics = Topic.objects.filter(Q(subject__icontains=search) & (Q(forum__category__chapter=user.chapter) | Q(forum__category__chapter__isnull=True))).order_by('forum__category__chapter', '-forum__category__exec_only', 'created_on')
		else:
			forums = Forum.objects.filter(Q(name__icontains=search) & ((Q(category__chapter=user.chapter) & Q(category__exec_only=False)) | (Q(category__chapter__isnull=True) & Q(category__exec_only=False)))).order_by('category__chapter', '-category__exec_only', 'created_on')
			topics = Topic.objects.filter(Q(subject__icontains=search) & ((Q(forum__category__chapter=user.chapter) & Q(forum__category__exec_only=False)) | (Q(forum__category__chapter__isnull=True) & Q(forum__category__exec_only=False)))).order_by('forum__category__chapter', 'created_on')
	return render_to_response('forums_search.html', {'chapter': c, 'search': search, 'forums': forums, 'topics': topics}, context_instance=RequestContext(request))
