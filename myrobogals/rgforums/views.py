from django.conf import settings
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
from myrobogals.rgforums.models import Category, Forum, Topic, Post, Vote, Offense, ForumSettings, PostFile
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient
from django.utils.http import urlquote, base36_to_int
from django.db.models import Avg, Max, Min, Count
import cgi

@login_required
def setmaxuploadfilesize(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	max_size_setting = None
	max_size = ''
	if request.user.is_superuser:
		max_size_setting = ForumSettings.objects.filter(key='maxuploadfilesize')
		if max_size_setting:
			max_size = max_size_setting[0].value
		if (request.method == 'POST') and ('maxfilesize' in request.POST):
			try:
				if max_size_setting:
					max_size_setting[0].value = str(int(request.POST['maxfilesize']))
					max_size_setting[0].save()
				else:
					max_file_size = ForumSettings()
					max_file_size.key = 'maxuploadfilesize'
					max_file_size.value = str(int(request.POST['maxfilesize']))
					max_file_size.save()
				if 'return' in request.GET:
					return HttpResponseRedirect(request.GET['return'])
				elif 'return' in request.POST:
					return HttpResponseRedirect(request.POST['return'])
				else:
					return HttpResponseRedirect('/forums/')
			except:
				msg = '- Maximum file size must be an integer'
				request.user.message_set.create(message=unicode(_(msg)))
		return render_to_response('forum_max_upload_file_size.html', {'max_size': max_size, 'return': request.GET['return'], 'apps': 'forums'}, context_instance=RequestContext(request))
	else:
		raise Http404

@login_required
def newcategory(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	global_user = False
	if request.user.is_superuser:
		global_user = True
	elif request.user.chapter.pk == 1 and request.user.is_staff:
		global_user = True
	if request.user.is_staff:
		if 'category' in request.GET and 'visibility' in request.GET and 'availability' in request.GET:
			if request.GET['category']:
				newCategory = Category()
				newCategory.name = request.GET['category']
				if request.GET['visibility']:
					if not global_user and request.user.chapter.pk != int(request.GET['visibility']):
						raise Http404  # Don't allow non-Global exec to create a category in another chapter
					newCategory.chapter = Group.objects.get(pk=request.GET['visibility'])
				elif not global_user:
					raise Http404  # Don't allow non-Global exec to create an international category
				if request.GET['availability'] == 'public':
					newCategory.exec_only = False
				elif request.GET['availability'] == 'execonly':
					newCategory.exec_only = True
				else:
					raise Http404
				if Category.objects.filter(name=newCategory.name, chapter=newCategory.chapter, exec_only=newCategory.exec_only):
					msg = _('- A similar category already exists')
					request.user.message_set.create(message=unicode(msg))
				else:
					newCategory.save()
			else:
				msg = '- The field "Category name" can not be empty.'
				request.user.message_set.create(message=unicode(_(msg)))
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			elif 'return' in request.POST:
				return HttpResponseRedirect(request.POST['return'])
			else:
				return HttpResponseRedirect('/forums/')
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
		if (request.method != 'POST') or ('delcategory' not in request.POST):
			return render_to_response('forum_categorydelete_confirm.html', {'category': c, 'return': request.GET['return']}, context_instance=RequestContext(request))
		else:
			chapter = c.chapter
			request.user.message_set.create(message=unicode(_('Category "%s" deleted') % cgi.escape(c.name)))
			c.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/')
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
		if (user.is_superuser) or (user.is_staff and (c == user.chapter)) or (user.is_staff and user.chapter.pk == 1 and c == None):
			if request.GET['forum'] and request.GET['description']:
				newForum = Forum()
				newForum.name = request.GET['forum']
				newForum.description = request.GET['description']
				newForum.category = g
				newForum.created_by = user
				if Forum.objects.filter(category=newForum.category, name=newForum.name):
					msg = '- A similar forum already exists'
					request.user.message_set.create(message=unicode(_(msg)))
				else:
					newForum.save()
			else:
				msg = '- The fields "Forum name" and "Description" can not be empty.'
				request.user.message_set.create(message=unicode(_(msg)))
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			elif 'return' in request.POST:
				return HttpResponseRedirect(request.POST['return'])
			else:
				return HttpResponseRedirect('/forums/')
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
	if ((not edit.category.chapter) and (not request.user.is_superuser and request.user.chapter.pk != 1)) or (edit.category.chapter and (((not request.user.is_staff) and (not request.user.is_superuser)) or ((c != request.user.chapter) and (not request.user.is_superuser)))):
		raise Http404
	if (request.method == 'POST'):
		if request.POST['forum'] and request.POST['description']:
			edit.name = request.POST['forum']
			edit.description = request.POST['description']
			edit.save()
		else:
			msg = '- The fields "new forum name" and "new description" can not be empty.'
			request.user.message_set.create(message=unicode(_(msg)))
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/')
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
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or (user not in f.blacklist.filter(pk=user.pk) and (((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
		f.watchers.add(user)
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/')
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
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or (user not in f.blacklist.filter(pk=user.pk) and (((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
		f.watchers.remove(user)
		for topic in f.topic_set.all():
			topic.watchers.remove(user)
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/')
	else:
		raise Http404

@login_required
def forums(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	editForum = ''
	globExecCategories = None
	globPubCategories = None
	localExecCategories = None
	localPubCategories = None

	# Get local categories (for superusers, show all local categories)
	if request.user.is_superuser:
		localPubCategories = Category.objects.filter(chapter__isnull=False, exec_only=False)
		localExecCategories = Category.objects.filter(chapter__isnull=False, exec_only=True)
	else:
		localPubCategories = Category.objects.filter(chapter=request.user.chapter, exec_only=False)
		if request.user.is_staff:
			localExecCategories = Category.objects.filter(chapter=request.user.chapter, exec_only=True)

	# Get global categories	
	if request.user.is_staff:
		globExecCategories = Category.objects.filter(chapter__isnull=True, exec_only=True)
	globPubCategories = Category.objects.filter(chapter__isnull=True, exec_only=False)

	if 'editForumId' in request.GET:
		edit = get_object_or_404(Forum, pk=request.GET['editForumId'])
		if ((not edit.category.chapter) and (not request.user.is_superuser and request.user.chapter.pk != 1)) or (edit.category.chapter and (((not request.user.is_staff) and (not request.user.is_superuser)) or ((edit.category.chapter != request.user.chapter) and (not request.user.is_superuser)))):
			raise Http404
		if edit.category.chapter != request.user.chapter:
			if not request.user.is_superuser:
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
	canDeleteGlobal = False
	canEditGlobal = False
	canAddGlobal = False
	if (request.user.is_staff and request.user.chapter.pk == 1) or request.user.is_superuser:
		canDeleteGlobal = True
		canEditGlobal = True
		canAddGlobal = True
	return render_to_response('forums.html', {'globExecCategories': globExecCategories, 'globPubCategories': globPubCategories, 'localExecCategories': localExecCategories, 'localPubCategories': localPubCategories, 'return': request.path, 'online_users': online_users, 'num_online_users': num_online_users, 'total_num_topics': total_num_topics, 'total_num_posts': total_num_posts, 'editForum': editForum, 'canDeleteGlobal': canDeleteGlobal, 'canEditGlobal': canEditGlobal, 'canAddGlobal': canAddGlobal}, context_instance=RequestContext(request))

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
	msg = '- '
	newTopicPk = None
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or (user not in f.blacklist.filter(pk=user.pk) and (((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
		if request.method == 'POST':
			topicform = NewTopicForm(request.POST, request.FILES)
			if topicform.is_valid():
				data = topicform.cleaned_data
				newTopic = Topic()
				newTopic.forum = f
				newTopic.posted_by = user
				newTopic.subject = data['subject']
				newTopic.last_post_time = datetime.datetime.now()
				newTopic.last_post_user = user
				fileWarning = False
				maxfilesize = 10
				maxfilesetting = ForumSettings.objects.filter(key='maxuploadfilesize')
				if maxfilesetting:
					maxfilesize = int(maxfilesetting[0].value)
				for upload_file in request.FILES.getlist('upload_files'):
					if (upload_file.size <= maxfilesize * 1024*1024) and (upload_file.name.__len__() <= 70):
						pass
					else:
						fileWarning = True
						msg += 'File: ' + cgi.escape(upload_file.name) + ' is not uploaded due to:'
						if (upload_file.size > maxfilesize * 1024*1024):
							msg = msg + ' File size exceeds ' + str(maxfilesize) + ' MB. '
						if (upload_file.name.__len__() > 70):
							msg = msg + ' File name exceeds 70 characters.'
						msg += '<br>'
				alreadyExistWarning = False
				if Topic.objects.filter(forum=newTopic.forum, subject=newTopic.subject):
					alreadyExistWarning = True
					msg += 'A similar topic already exists.'
				if alreadyExistWarning or fileWarning:
					request.user.message_set.create(message=unicode(_(msg)))
				else:
					newTopic.save()
					newTopicPk = newTopic.pk
					postMessage = Post()
					postMessage.topic = newTopic
					postMessage.posted_by = user
					postMessage.message = data['message']
					postMessage.save()
					for upload_file in request.FILES.getlist('upload_files'):
						pf = PostFile(postfile=upload_file)
						pf.save()
						postMessage.upload_files.add(pf)
					postMessage.save()
					f.last_post_time = datetime.datetime.now()
					f.last_post_user = user
					f.save()
					if 'watch' in request.POST:
						if request.POST['watch'] == '1':
							if not f.watchers.filter(pk=user.pk):
								newTopic.watchers.add(user)
					else:
						if f.watchers.filter(pk=user.pk):
							f.watchers.remove(user)
							for topic in f.topic_set.all():
								if topic != newTopic:
									topic.watchers.add(user)
								else:
									topic.watchers.remove(user)
						else:
							newTopic.watchers.remove(user)
					watchers_list = f.watchers.all().exclude(pk=request.user.pk)
					watchers = []
					for watcher in watchers_list:
						if (watcher.is_superuser) or (watcher.is_staff and ((c == watcher.chapter) or (c == None))) or (watcher not in f.blacklist.filter(pk=watcher.pk) and (((c == watcher.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
							watchers.append(watcher)
						else:
							f.watchers.remove(watcher)
							for topic in f.topic_set.all():
								topic.watchers.remove(watcher)
					if watchers:
						message = EmailMessage()
						message.subject = 'New Topic: ' + newTopic.subject
						message.body = 'New topic for forum "' + cgi.escape(f.name) + '" in category "' + cgi.escape(g.name) +'"<br><br>Topic subject: ' + cgi.escape(newTopic.subject) + ' (started by ' + newTopic.posted_by.get_full_name() + ')<br><br>Topic Message:<br>' + cgi.escape(postMessage.message).replace("\n","<br>") + '<br><br>--<br>{{unwatchall}}'
						message.from_name = "myRobogals"
						message.from_address = "my@robogals.org"
						message.reply_address = "my@robogals.org"
						message.sender = User.objects.get(username='edit')
						message.html = True
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
				request.user.message_set.create(message=unicode(_('- The fields "New Topic" and "Message" can not be empty.')))
		else:
			raise Http404
		if 'return' in request.GET:
			if newTopicPk:
				return HttpResponseRedirect(request.GET['return'] + '&targettopicpk=' + str(newTopicPk))
			else:
				return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/forum/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def downloadpostfile(request, post_id, file_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	post = get_object_or_404(Post, pk=post_id)
	user = request.user
	t = post.topic
	f = t.forum
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or (user not in f.blacklist.filter(pk=user.pk) and (((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
		if post.upload_files.filter(pk=file_id):
			try:
				postfile = post.upload_files.get(pk=file_id)
				response = HttpResponse(postfile.postfile.read(), content_type='application/octet-stream')
				response['Content-Disposition'] = 'attachment; filename="%s"' % postfile.filename()
				response['Content-Length'] = postfile.filesize()
				return response
			except:
				request.user.message_set.create(message=unicode(_('- File: "%s" does not exist' % cgi.escape(postfile.filename()))))
				if 'return' in request.GET:
					return HttpResponseRedirect(request.GET['return'])
				else:
					return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')
		else:
			request.user.message_set.create(message=unicode(_('- File does not exist')))
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			else:
				return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')
	else:
		raise Http404

@login_required
def stickytopic(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	if request.method == 'POST':
		t = None
		for topic_id in request.POST:
			topic = get_object_or_404(Topic, pk=topic_id)
			f = topic.forum
			g = f.category
			c = g.chapter
			if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None):
				topic.sticky = False if topic.sticky else True
				topic.save()
				t = topic
			else:
				raise Http404
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/forum/' + str(t.forum.pk) + '/')
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
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or (user not in f.blacklist.filter(pk=user.pk) and (((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
		if not f.watchers.filter(pk=user.pk):
			t.watchers.add(user)
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/forum/' + str(f.pk) + '/')
	else:
		raise Http404

def unwatchall(request, uidb36, token, step):
	if step == '1':
		return render_to_response('response.html', {'next_url': '/forums/unwatchall/' + uidb36 + '/' + token + '/2/', 'msg': 'Are you sure you want to empty watch list?'}, context_instance=RequestContext(request))
	elif step == '2':
		try:
			uid_int = base36_to_int(uidb36)
		except ValueError:
			raise Http404

		user = get_object_or_404(User, id=uid_int)
		try:
			ts_b36, hash = token.split("-")
			ts = base36_to_int(ts_b36)
		except ValueError:
			return render_to_response('response.html', {'msg': 'The link is invalid!'}, context_instance=RequestContext(request))

		from django.utils.hashcompat import sha_constructor
		hash2 = sha_constructor(unicode(user.id) + unicode(ts)).hexdigest()[::2]

		if (hash2 != hash) or (((datetime.date.today() - datetime.date(2001,1,1)).days - ts) > settings.PASSWORD_RESET_TIMEOUT_DAYS):
			return render_to_response('response.html', {'msg': 'The link is invalid!'}, context_instance=RequestContext(request))

		for f in user.forum_watchers.all():
			f.watchers.remove(user)
		for t in user.topic_watchers.all():
			t.watchers.remove(user)
		return render_to_response('response.html', {'msg': 'Watch list is emptied!'}, context_instance=RequestContext(request))
	else:
		return render_to_response('response.html', {'msg': 'The link is invalid!'}, context_instance=RequestContext(request))

@login_required
def unwatchalltopics(request):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	for f in request.user.forum_watchers.all():
		f.watchers.remove(request.user)
	for t in request.user.topic_watchers.all():
		t.watchers.remove(request.user)
	request.user.message_set.create(message=unicode(_('Your watch list is emptied')))
	if 'return' in request.GET:
		return HttpResponseRedirect(request.GET['return'])
	elif 'return' in request.POST:
		return HttpResponseRedirect(request.POST['return'])
	else:
		return HttpResponseRedirect('/forums/')

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
			if (not f.watchers.filter(pk=user.pk)) and (user not in f.blacklist.filter(pk=user.pk)):
				t.watchers.add(user)
	request.user.message_set.create(message=unicode(_('Topics with your posts have been added to your watch list')))
	if 'return' in request.GET:
		return HttpResponseRedirect(request.GET['return'])
	elif 'return' in request.POST:
		return HttpResponseRedirect(request.POST['return'])
	else:
		return HttpResponseRedirect('/forums/')


@login_required
def unwatchtopic(request, topic_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	t = get_object_or_404(Topic, pk=topic_id)
	f = t.forum
	g = f.category
	c = g.chapter
	user = request.user
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or (user not in f.blacklist.filter(pk=user.pk) and (((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
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
		else:
			return HttpResponseRedirect('/forums/forum/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def deleteforum(request, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None):
		if (request.method != 'POST') or ('delforum' not in request.POST):
			return render_to_response('forum_delete_confirm.html', {'forum': f, 'return': request.GET['return']}, context_instance=RequestContext(request))
		else:
			chapter = c
			request.user.message_set.create(message=unicode(_('Forum "' + cgi.escape(f.name) + '" deleted')))
			f.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/')
	else:
		raise Http404

@login_required
def viewforum(request, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	topicsPerPage = 3
	pageNumber = request.GET.get('page', None)
	if (not pageNumber) and (request.COOKIES.get('forumpk', None)==str(f.pk)):
		pageNumber = request.COOKIES.get('forumpage')
	# If the forum is "owned" by a chapter, ensure that this user is a member of that chapter or a superuser
	if c and c != request.user.chapter and not request.user.is_superuser:
		raise Http404
	# If the forum is for exec only, check that they are exec
	if g.exec_only and not request.user.is_staff:
		raise Http404
	topicform = NewTopicForm()
	sort = request.GET.get('sort', None)
	if (not sort) and (request.COOKIES.get('forumpk', None)==str(f.pk)):
		sort = request.COOKIES.get('forumsort')
	if sort == 'votes_up':
		topics_list = f.topic_set.all().annotate(numvotes=Count('vote')).order_by('-sticky', 'numvotes')
	elif sort == 'votes_down':
		topics_list = f.topic_set.all().annotate(numvotes=Count('vote')).order_by('-sticky', '-numvotes')
	elif sort == 'topics_up':
		topics_list = f.topic_set.all().order_by('-sticky', 'subject')
	elif sort == 'topics_down':
		topics_list = f.topic_set.all().order_by('-sticky', '-subject')
	elif sort == 'replies_up':
		topics_list = f.topic_set.all().annotate(numreplies=Count('post')).order_by('-sticky', 'numreplies')
	elif sort == 'replies_down':
		topics_list = f.topic_set.all().annotate(numreplies=Count('post')).order_by('-sticky', '-numreplies')
	elif sort == 'views_up':
		topics_list = f.topic_set.all().order_by('-sticky', 'num_views')
	elif sort == 'views_down':
		topics_list = f.topic_set.all().order_by('-sticky', '-num_views')
	elif sort == 'last_post_up':
		topics_list = f.topic_set.all().order_by('-sticky', 'last_post_time')
	elif sort == 'last_post_down':
		topics_list = f.topic_set.all().order_by('-sticky', '-last_post_time')
	else:
		sort = 'last_post_down'
		topics_list = f.topic_set.all().order_by('-sticky', '-last_post_time')
	if ('targettopicpk' in request.GET):
		index = 0
		found = False
		for topic in topics_list:
			if str(topic.pk) == request.GET['targettopicpk']:
				found = True
				break
			else:
				index += 1
		if found:
			pageNumber = int(index) / int(topicsPerPage) + 1
	paginator = Paginator(topics_list, topicsPerPage)
	page = pageNumber
	try:
		topics = paginator.page(page)
	except EmptyPage:
		topics = paginator.page(paginator.num_pages)
		page = paginator.num_pages
	except:
		topics = paginator.page(1)
		page = 1
	if request.user.is_superuser or (request.user.is_staff and c == request.user.chapter) or (request.user.is_staff and request.user.chapter.pk == 1 and c == None):
		can_delete = True
	else:
		can_delete = False
	response = render_to_response('forum_view.html', {'chapter': c, 'topics': topics, 'topicform': topicform, 'forum': f, 'returnFromNewTopic': request.path + '?' + 'page=' + str(page) + '&sort=' + sort, 'return': request.path + '?' + 'page=' + str(page) + '&sort=' + sort, 'can_delete': can_delete, 'sort': sort}, context_instance=RequestContext(request))
	cookie_life = 300
	response.set_cookie("forumpage", page, max_age=cookie_life)
	response.set_cookie("forumsort", sort, max_age=cookie_life)
	response.set_cookie("forumpk", f.pk, max_age=cookie_life)
	return response

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
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None) or (user == p.posted_by):
		if (request.method != 'POST') or ('delpost' not in request.POST):
			return render_to_response('forum_postdelete_confirm.html', {'post': p, 'return': request.GET['return']}, context_instance=RequestContext(request))
		else:
			p.delete()
			last_post_topic = Post.objects.filter(topic=t).latest('created_on')
			t.last_post_time = last_post_topic.created_on
			t.last_post_user = last_post_topic.posted_by
			t.num_views = t.num_views - 1
			t.save()
			last_post_forum = Post.objects.filter(topic__forum=f).latest('created_on')
			f.last_post_time = last_post_forum.created_on
			f.last_post_user = last_post_forum.posted_by
			f.save()
			request.user.message_set.create(message=unicode(_('Post deleted')))
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			elif 'return' in request.POST:
				return HttpResponseRedirect(request.POST['return'])
			else:
				return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')
	else:
		raise Http404

class WritePostForm(forms.Form):
	message = forms.CharField(widget=TinyMCE(attrs={'cols': 65}))

@login_required
def topicundoupvote(request, post_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	p = get_object_or_404(Post, pk=post_id)
	t = p.topic
	f = t.forum
	g = f.category
	c = g.chapter
	if f.blacklist.filter(pk=user.pk):
		raise Http404
	# If the forum is "owned" by a chapter, ensure that this user is a member of that chapter or a superuser
	if c and c != request.user.chapter and not request.user.is_superuser:
		raise Http404
	# If the forum is for exec only, check that they are exec
	if g.exec_only and not request.user.is_staff:
		raise Http404
	exist_vote = Vote.objects.filter(topic=t, voter=user)
	for v in exist_vote:
		v.delete()
	if 'return' in request.GET:
		return HttpResponseRedirect(request.GET['return'])
	elif 'return' in request.POST:
		return HttpResponseRedirect(request.POST['return'])
	else:
		return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')

@login_required
def topicupvote(request, post_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	p = get_object_or_404(Post, pk=post_id)
	t = p.topic
	f = t.forum
	g = f.category
	c = g.chapter
	if f.blacklist.filter(pk=user.pk):
		raise Http404
	# If the forum is "owned" by a chapter, ensure that this user is a member of that chapter or a superuser
	if c and c != request.user.chapter and not request.user.is_superuser:
		raise Http404
	# If the forum is for exec only, check that they are exec
	if g.exec_only and not request.user.is_staff:
		raise Http404
	exist_vote = Vote.objects.filter(topic=t, voter=user)
	if exist_vote:
		request.user.message_set.create(message=unicode(_('- You have already voted for this topic')))
	else:
		vote = Vote()
		vote.topic = t
		vote.voter = user
		vote.save()
	if 'return' in request.GET:
		return HttpResponseRedirect(request.GET['return'])
	elif 'return' in request.POST:
		return HttpResponseRedirect(request.POST['return'])
	else:
		return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')

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
	warning = False
	msg = '- '
	maxfilesize = 10
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None) or (p.posted_by == user and (user not in f.blacklist.filter(pk=user.pk))):
		if (request.method == 'POST'):
			postform = WritePostForm(request.POST, request.FILES)
			maxfilesetting = ForumSettings.objects.filter(key='maxuploadfilesize')
			if maxfilesetting:
				maxfilesize = int(maxfilesetting[0].value)
			for upload_file in request.FILES.getlist('upload_files'):
				if (upload_file.size <= maxfilesize * 1024*1024) and (upload_file.name.__len__() <= 70):
					pass
				else:
					warning = True
					msg += 'File: ' + cgi.escape(upload_file.name) + ' is not uploaded due to:'
					if (upload_file.size > maxfilesize * 1024*1024):
						msg = msg + ' File size exceeds ' + str(maxfilesize) + ' MB. '
					if (upload_file.name.__len__() > 70):
						msg = msg + ' File name exceeds 70 characters.'
					msg += '<br>'
			if postform.is_valid() and (not warning):
				data = postform.cleaned_data
				p.message = data['message']
				p.updated_on = datetime.datetime.now()
				p.edited_by = user
				p.save()
				for upload_file in request.FILES.getlist('upload_files'):
					pf = PostFile(postfile=upload_file)
					pf.save()
					p.upload_files.add(pf)
				p.save()
				t.num_views = t.num_views - 1
				t.save()
				if 'Watch' in request.POST:
					if not f.watchers.filter(pk=user.pk):
						t.watchers.add(user)
				else:
					if f.watchers.filter(pk=user.pk):
						f.watchers.remove(user)
						for topic in f.topic_set.all():
							if topic != t:
								topic.watchers.add(user)
							else:
								topic.watchers.remove(user)
					else:
						t.watchers.remove(user)
			else:
				if not postform.is_valid():
					msg += 'The field "Message" can not be empty.'
				request.user.message_set.create(message=unicode(_(msg)))
				warning = True
			if 'return' in request.GET:
				if warning:
					ret = request.GET['return'].rsplit('#',1)[0]
				else:
					ret = request.GET['return']
				return HttpResponseRedirect(ret)
			elif 'return' in request.POST:
				if warning:
					ret = request.POST['return'].rsplit('#',1)[0]
				else:
					ret = request.POST['return']
				return HttpResponseRedirect(ret)
			else:
				return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')
		else:
			raise Http404
	else:
		raise Http404

@login_required
def blacklistuser(request, forum_id, user_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	perpetrator = get_object_or_404(User, pk=user_id)
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	if perpetrator.is_staff:
		msg = _('- Warning: %s is a staff, therefore can not be blacklisted!') % perpetrator.get_full_name()
		request.user.message_set.create(message=unicode(msg))
		return HttpResponseRedirect('/forums/showforumoffenses/' + str(f.pk) + '/')
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None):
		f.blacklist.add(perpetrator)
		f.watchers.remove(perpetrator)
		for topic in f.topic_set.all():
			topic.watchers.remove(perpetrator)
		return HttpResponseRedirect('/forums/showforumoffenses/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def unblacklistuser(request, forum_id, user_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	perpetrator = get_object_or_404(User, pk=user_id)
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None):
		f.blacklist.remove(perpetrator)
		return HttpResponseRedirect('/forums/showforumoffenses/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def showforumoffenses(request, forum_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	f = get_object_or_404(Forum, pk=forum_id)
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None):
		offens = Offense.objects.filter(forum=f)
		offens_list = []
		for offen in offens:
			if request.user.is_superuser:
				offens_list.append((True, offen, Post.objects.filter(posted_by = offen.perpetrator).count(), 'online' if (offen.perpetrator.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
			elif offen.perpetrator.privacy >= 20:
				offens_list.append((True, offen, Post.objects.filter(posted_by = offen.perpetrator).count(), 'online' if (offen.perpetrator.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
			elif offen.perpetrator.privacy >= 10:
				if not request.user.is_authenticated():
					offens_list.append((False, offen))
				else:
					offens_list.append((True, offen, Post.objects.filter(posted_by = offen.perpetrator).count(), 'online' if (offen.perpetrator.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
			elif offen.perpetrator.privacy >= 5:
				if not request.user.is_authenticated():
					offens_list.append((False, offen))
				elif not (request.user.chapter == offen.perpetrator.chapter):
					offens_list.append((False, offen))
				else:
					offens_list.append((True, offen, Post.objects.filter(posted_by = offen.perpetrator).count(), 'online' if (offen.perpetrator.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
			else:
				if not request.user.is_authenticated():
					offens_list.append((False, offen))
				elif not (request.user.chapter == offen.perpetrator.chapter):
					offens_list.append((False, offen))
				elif not request.user.is_staff:
					offens_list.append((False, offen))
				else:
					offens_list.append((True, offen, Post.objects.filter(posted_by = offen.perpetrator).count(), 'online' if (offen.perpetrator.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
		return render_to_response('forums_offenses.html', {'chapter': c, 'offens_list': offens_list, 'forum': f}, context_instance=RequestContext(request))
	else:
		raise Http404

class WriteOffenseForm(forms.Form):
	notes = forms.CharField(widget=TinyMCE(attrs={'cols': 65}))

@login_required
def fileoffenses(request, post_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	p = get_object_or_404(Post, pk=post_id)
	t = p.topic
	f = t.forum
	g = f.category
	c = g.chapter
	warning = False
	msg = ''
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None):
		if request.method == 'POST':
			offenseForm = WriteOffenseForm(request.POST)
			if offenseForm.is_valid():
				data = offenseForm.cleaned_data
				offen = Offense()
				offen.forum = f
				offen.officer = user
				offen.perpetrator = p.posted_by
				offen.notes = data['notes']
				offen.save()
				if 'blackList' in request.POST:
					if (request.POST['blackList'] == '1'):
						if (not offen.perpetrator.is_staff):
							f.blacklist.add(p.posted_by)
							f.watchers.remove(p.posted_by)
							for topic in f.topic_set.all():
								topic.watchers.remove(p.posted_by)
						else:
							msg = _('- Warning: %s is a staff, therefore can not be blacklisted!') % offen.perpetrator.get_full_name()
							request.user.message_set.create(message=unicode(msg))
							warning = True
				if 'deletePost' in request.POST:
					if request.POST['deletePost'] == '1':
						p.delete()
				if 'return' in request.POST:
					if warning:
						ret = request.POST['return'].rsplit('#',1)[0]
					else:
						ret = request.POST['return']
					return HttpResponseRedirect(ret)
				elif 'return' in request.GET:
					if warning:
						ret = request.GET['return'].rsplit('#',1)[0]
					else:
						ret = request.GET['return']
					return HttpResponseRedirect(ret)
				else:
					return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')
		else:
			offenseForm = WriteOffenseForm({'notes': 'Category: ' + g.name + '\nForum: ' + f.name + '\nTopic: ' + t.subject + '\nOffensive message:\n' + p.get_quote()})
		if 'return' in request.GET:
			returnPath = request.GET['return']
		elif 'return' in request.POST:
			returnPath = request.POST['return']
		else:
			returnPath = ''
		return render_to_response('offense_write.html', {'offenseForm': offenseForm, 'return': returnPath, 'post': p}, context_instance=RequestContext(request))
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
	if (user.is_superuser) or (user.is_staff and ((c == user.chapter) or (c == None))) or (user not in f.blacklist.filter(pk=user.pk) and (((c == user.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
		if request.method == 'POST':
			postform = WritePostForm(request.POST, request.FILES)
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
				if 'watch' in request.POST:
					if request.POST['watch'] == '1':
						if not f.watchers.filter(pk=user.pk):
							t.watchers.add(user)
				else:
					if f.watchers.filter(pk=user.pk):
						f.watchers.remove(user)
						for topic in f.topic_set.all():
							if topic != t:
								topic.watchers.add(user)
							else:
								topic.watchers.remove(user)
					else:
						t.watchers.remove(user)
				watchers_list = (f.watchers.all() | t.watchers.all()).distinct().exclude(pk=request.user.pk)
				watchers = []
				for watcher in watchers_list:
					if (watcher.is_superuser) or (watcher.is_staff and ((c == watcher.chapter) or (c == None))) or (watcher not in f.blacklist.filter(pk=watcher.pk) and (((c == watcher.chapter) and (g.exec_only == False)) or ((c == None) and (g.exec_only == False)))):
						watchers.append(watcher)
					else:
						f.watchers.remove(watcher)
						for topic in f.topic_set.all():
							topic.watchers.remove(watcher)
				if watchers:
					message = EmailMessage()
					message.subject = 'New Post for topic "' + t.subject + '"'
					message.body = 'New post for topic "' + cgi.escape(t.subject) + '" for forum "' + cgi.escape(f.name) + '" in category "' + cgi.escape(g.name) + '"<br><br>Post message: (posted by ' + postMessage.posted_by.get_full_name() + ')<br>' + cgi.escape(postMessage.message).replace("\n","<br>") + '<br><br>--<br>{{unwatchall}}'
					message.from_name = "myRobogals"
					message.from_address = "my@robogals.org"
					message.reply_address = "my@robogals.org"
					message.sender = User.objects.get(username='edit')
					message.html = True
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
				request.user.message_set.create(message=unicode(_('- The field "Message" can not be empty.')))
		else:
			raise Http404
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')
	else:
		raise Http404

@login_required
def deletetopic(request, topic_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	t = get_object_or_404(Topic, pk=topic_id)
	f = t.forum
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None) or (user == t.posted_by):
		if (request.method != 'POST') or ('deltopic' not in request.POST):
			return render_to_response('forum_topicdelete_confirm.html', {'topic': t, 'return': request.GET['return']}, context_instance=RequestContext(request))
		else:
			chapter = f.category.chapter
			request.user.message_set.create(message=unicode(_('Topic "%s" deleted') % cgi.escape(t.subject)))
			t.delete()
			all_posts = Post.objects.filter(topic__forum=f)
			if all_posts:
				last_post_forum = all_posts.latest('created_on')
				f.last_post_time = last_post_forum.created_on
				f.last_post_user = last_post_forum.posted_by
			else:
				f.last_post_time = None
				f.last_post_user = None
			f.save()
			if 'return' in request.GET:
				return HttpResponseRedirect(request.GET['return'])
			elif 'return' in request.POST:
				return HttpResponseRedirect(request.POST['return'])
			else:
				return HttpResponseRedirect('/forums/forum/' + str(f.pk) + '/')
	else:
		raise Http404

@login_required
def viewtopic(request, topic_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	t = get_object_or_404(Topic, pk=topic_id)
	f = t.forum
	g = f.category
	c = g.chapter
	# If the forum is "owned" by a chapter, ensure that this user is a member of that chapter or a superuser
	if c and c != request.user.chapter and not request.user.is_superuser:
		raise Http404
	# If the forum is for exec only, check that they are exec
	if g.exec_only and not request.user.is_staff:
		raise Http404
	editPost = ''
	if ('quotePostId' in request.GET) and ('editPostId' not in request.GET):
		quote = Post.objects.get(pk=request.GET['quotePostId'])
		if quote.topic.pk != t.pk:
			raise Http404
		postform = WritePostForm({'message': quote.get_quote()})
	elif ('editPostId' in request.GET) and ('quotePostId' not in request.GET):
		edit = Post.objects.get(pk=request.GET['editPostId'])
		if not request.user.is_superuser and edit.posted_by != request.user:
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
				posts_list.append((False, post, Post.objects.filter(posted_by = post.posted_by).count()))
			else:
				posts_list.append((True, post, Post.objects.filter(posted_by = post.posted_by).count(), 'online' if (post.posted_by.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
		elif post.posted_by.privacy >= 5:
			if not request.user.is_authenticated():
				posts_list.append((False, post, Post.objects.filter(posted_by = post.posted_by).count()))
			elif not (request.user.chapter == post.posted_by.chapter):
				posts_list.append((False, post, Post.objects.filter(posted_by = post.posted_by).count()))
			else:
				posts_list.append((True, post, Post.objects.filter(posted_by = post.posted_by).count(), 'online' if (post.posted_by.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
		else:
			if not request.user.is_authenticated():
				posts_list.append((False, post, Post.objects.filter(posted_by = post.posted_by).count()))
			elif not (request.user.chapter == post.posted_by.chapter):
				posts_list.append((False, post, Post.objects.filter(posted_by = post.posted_by).count()))
			elif not request.user.is_staff:
				posts_list.append((False, post, Post.objects.filter(posted_by = post.posted_by).count()))
			else:
				posts_list.append((True, post, Post.objects.filter(posted_by = post.posted_by).count(), 'online' if (post.posted_by.forum_last_act > (datetime.datetime.now()-datetime.timedelta(hours=1))) else 'offline'))
	paginator = Paginator(posts_list, 3)
#	paginator = Paginator(posts_list, 10)
	page = request.GET.get('page')
	try:
		posts = paginator.page(page)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
		page = paginator.num_pages
	except:
		posts = paginator.page(1)
		page = 1
	if request.user.is_superuser or (request.user.is_staff and c == request.user.chapter) or (request.user.is_staff and request.user.chapter.pk == 1 and c == None):
		canDelete = True
		canEdit = True
		canFileOffenses = True
	else:
		canDelete = False
		canEdit = False
		canFileOffenses = False
	if Vote.objects.filter(topic=t, voter=request.user):
		hasAlreadyVoted = True
	else:
		hasAlreadyVoted = False
	forumpage = request.GET.get('forumpage') if request.GET.get('forumpage') else ''
	forumsort = request.GET.get('forumsort') if request.GET.get('forumsort') else ''
	return render_to_response('topic_view.html', {'chapter': c, 'posts': posts, 'postform': postform, 'topic': t, 'forum': f, 'editPost': editPost, 'returnLastPage': request.path + '?' + 'page=' + '-1' + '&forumpage=' + forumpage + '&forumsort=' + forumsort, 'return': request.path + '?' + 'page=' + str(page) + '&forumpage=' + forumpage + '&forumsort=' + forumsort, 'canDelete': canDelete, 'canEdit': canEdit, 'canFileOffenses': canFileOffenses, 'hasAlreadyVoted': hasAlreadyVoted, 'forumsort': forumsort, 'forumpage': forumpage}, context_instance=RequestContext(request))

@login_required
def deletefile(request, post_id, file_id):
	request.user.forum_last_act = datetime.datetime.now()
	request.user.save()
	user = request.user
	p = get_object_or_404(Post, pk=post_id)
	t = p.topic
	f = t.forum
	g = f.category
	c = g.chapter
	if (user.is_superuser) or (user.is_staff and c == user.chapter) or (user.is_staff and user.chapter.pk == 1 and c == None) or (p.posted_by == user and (user not in f.blacklist.filter(pk=user.pk))):
		file_to_delete = p.upload_files.get(pk=file_id)
		if file_to_delete:
			if (request.method != 'POST') or ('delpostfile' not in request.POST):
				return render_to_response('forum_postfiledelete_confirm.html', {'post': p, 'file_id': int(file_id), 'return': request.GET['return']}, context_instance=RequestContext(request))
			else:
				p.upload_files.remove(file_to_delete)
				file_to_delete.postfile.delete()
				file_to_delete.delete()
		if 'return' in request.GET:
			return HttpResponseRedirect(request.GET['return'])
		elif 'return' in request.POST:
			return HttpResponseRedirect(request.POST['return'])
		else:
			return HttpResponseRedirect('/forums/topic/' + str(t.pk) + '/')
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
