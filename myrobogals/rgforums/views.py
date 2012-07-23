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

@login_required
def newcategory(request):
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
	if request.user.is_superuser:
		c = get_object_or_404(Category, pk=category_id)
		chapter = c.chapter
		request.user.message_set.create(message=unicode(_('Category "' + c.name + '" deleted')))
		c.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif chapter:
			return HttpResponseRedirect('/forums/' + chapter.myrobogals_url + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def newforum(request):
	if 'forum' in request.GET and 'category' in request.GET:
		user = request.user
		g = get_object_or_404(Category, pk=request.GET['category'])
		c = g.chapter
		if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
			if request.GET['forum']:
				newForum = Forum()
				newForum.name = request.GET['forum']
				newForum.category = g
				newForum.updated_on = datetime.datetime.now()
				if Forum.objects.filter(category=newForum.category, name=newForum.name):
					msg = 'A similar forum already exists'
					request.user.message_set.create(message=unicode(_(msg)))
				else:
					newForum.save()
			else:
				msg = 'The field "Forum name" can not be empty'
				request.user.message_set.create(message=unicode(_(msg)))
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			elif c:
				return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/')
			else:
				return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
		else:
			raise Http404
	else:
		raise Http404

@login_required
def forums(request, chapterurl):
	c = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
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
	return render_to_response('forums.html', {'chapter': c, 'globExecCategories': globExecCategories, 'globPubCategories': globPubCategories, 'localExecCategories': localExecCategories, 'localPubCategories': localPubCategories, 'return': request.path + '?' + request.META['QUERY_STRING'], 'user': request.user}, context_instance=RequestContext(request))

class NewTopicForm(forms.Form):
	subject = forms.CharField(label=_('New Topic:'), max_length=64)
	message = forms.CharField(label=_('Message:'), widget=TinyMCE(attrs={'cols': 50}))

@login_required
def newtopic(request, forum_id):
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
				newTopic.last_post = '%s\nby %s' % (str(datetime.datetime.now()).split('.')[0], user.get_full_name())
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
					f.num_posts = f.num_posts + 1
					f.last_post = '%s\nby %s' % (str(datetime.datetime.now()).split('.')[0], user.get_full_name())
					f.num_topics = f.num_topics + 1
	#				f.updated_on = datetime.datetime.now()
					f.save()
			else:
				request.user.message_set.create(message=unicode(_('The fields "New Topic" and "Message" can not be empty')))
		else:
			raise Http404
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/forum/' + str(f.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def deleteforum(request, forum_id):
	if request.user.is_superuser:
		f = get_object_or_404(Forum, pk=forum_id)
		chapter = f.category.chapter
		request.user.message_set.create(message=unicode(_('Forum "' + f.name + '" deleted')))
		f.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif chapter:
			return HttpResponseRedirect('/forums/' + chapter.myrobogals_url + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def viewforum(request, chapterurl, forum_id):
	chapterHome = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	user = request.user
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		topicform = NewTopicForm(None)
		topics_list = f.topic_set.all()
		paginator = Paginator(topics_list, 6)
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

class WritePostForm(forms.Form):
	message = forms.CharField(widget=TinyMCE(attrs={'cols': 50}))

@login_required
def newpost(request, topic_id):
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
				t.num_replies = t.num_replies + 1
				t.last_post = '%s\nby %s' % (str(datetime.datetime.now()).split('.')[0], user.get_full_name())
				t.num_views = t.num_views - 1
				t.save()
				f.num_posts = f.num_posts + 1
				f.last_post = '%s\nby %s' % (str(datetime.datetime.now()).split('.')[0], user.get_full_name())
				f.updated_on = datetime.datetime.now()
				f.save()
			else:
				request.user.message_set.create(message=unicode(_('The fields "Message" can not be empty')))
		else:
			raise Http404
		if 'return' in request.GET:
#			return HttpResponseRedirect(re.sub('&*postId=\d+&*', '', request.GET['return']))
			return HttpResponseRedirect(request.GET['return'])
		elif c:
			return HttpResponseRedirect('/forums/' + c.myrobogals_url + '/topic/' + str(t.pk) + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/topic/' + str(t.pk) + '/')
	else:
		raise Http404

@login_required
def deletetopic(request, topic_id):
	if request.user.is_superuser:
		t = get_object_or_404(Topic, pk=topic_id)
		t.forum.num_topics = t.forum.num_topics - 1
		t.forum.num_posts = t.forum.num_posts - t.num_replies - 1
		t.forum.save()
		chapter = t.forum.category.chapter
		request.user.message_set.create(message=unicode(_('Topic "' + t.subject + '" deleted')))
		t.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif chapter:
			return HttpResponseRedirect('/forums/' + chapter.myrobogals_url + '/')
		else:
			return HttpResponseRedirect('/forums/' + request.user.chapter.myrobogals_url + '/')
	else:
		raise Http404

@login_required
def viewtopic(request, chapterurl, topic_id):
	chapterHome = get_object_or_404(Group, myrobogals_url__exact=chapterurl)
	user = request.user
	t = get_object_or_404(Topic, pk=topic_id)
	f = t.forum
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or ((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)):
		if request.GET.get('postId', False):
			quote = Post.objects.get(pk=request.GET['postId'])
			postform = WritePostForm({'message': quote.get_quote()})
		else:
			postform = WritePostForm(None)
			t.num_views = t.num_views + 1
			t.save()
		posts_list = t.post_set.all()
		paginator = Paginator(posts_list, 6)
		page = request.GET.get('page')
		try:
			posts = paginator.page(page)
		except EmptyPage:
			posts = paginator.page(paginator.num_pages)
		except:
			posts = paginator.page(1)
		return render_to_response('topic_view.html', {'chapter': c, 'posts': posts, 'postform': postform, 'topic': t, 'chapterHome': chapterHome, 'forum': f, 'return': request.path + '?' + 'page=' + '-1'}, context_instance=RequestContext(request))
	else:
		raise Http404

@login_required
def search(request):
	search = ''
	forums = None
	topics = None
	user = request.user
	if 'search' in request.GET:
		search = request.GET['search']
		if user.is_superuser:
			forums = Forum.objects.filter(Q(name__icontains=search))
			topics = Topic.objects.filter(Q(subject__icontains=search))
		elif user.is_staff:
			forums = Forum.objects.filter(Q(name__icontains=search) & (Q(category__chapter=user.chapter) | Q(category__chapter__isnull=True)))
			topics = Topic.objects.filter(Q(subject__icontains=search) & (Q(forum__category__chapter=user.chapter) | Q(forum__category__chapter__isnull=True)))
		else:
			forums = Forum.objects.filter(Q(name__icontains=search) & ((Q(category__chapter=user.chapter) & Q(category__exec_only=False)) | (Q(category__chapter__isnull=True) & Q(category__exec_only=False))))
			topics = Topic.objects.filter(Q(subject__icontains=search) & ((Q(forum__category__chapter=user.chapter) & Q(forum__category__exec_only=False)) | (Q(forum__category__chapter__isnull=True) & Q(forum__category__exec_only=False))))
	return render_to_response('forums_search.html', {'chapter': request.user.chapter, 'search': search, 'forums': forums, 'topics': topics}, context_instance=RequestContext(request))
