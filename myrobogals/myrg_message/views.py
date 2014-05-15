from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from myrg_message.models import Message, MessageDefinition
from myrg_message.serializers import MessageSerializer, MessageDefinitionSerializer
from myrg_users.models import RobogalsUser
from myrg_groups.models import RoleType, Role

import base64
import mandrill

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class MessageDefinitionViewSet(viewsets.ModelViewSet):
    queryset = MessageDefinition.objects.all()
    serializer_class = MessageDefinitionSerializer

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

# Error checking is rely on the fact that exceptions
# will be through for "var['key']" if 'key' is not in
# the dict "var", database entries "msg_def_record" and
# "msg_record" will be stored if no exception is thrown.
# Each request to mandrill contains no more than
# "recipients_per_req" recipients. If any one request
# to mandrill throws exception, all subsequent requests will be
# aborted, but database entries "msg_def_record" and
# "msg_record" will still be stored in disk, for future
# retry.
def send_email(sender, recipients, message):
    mandrill_client = mandrill.Mandrill('HGjH3nx8VBhbdiYqymkYZQ')
    sender_user = get_object_or_404(RobogalsUser, pk=sender['user'])
    sender_role = get_object_or_404(Role, pk=sender['role'])
    msg = {'from_email': sender_user.primary_email}
    if 'name' in sender:
        msg['from_name'] = sender['name']
    else:
        msg['from_name'] = sender_user.get_full_name()
    if not recipients:
        raise Http404
    for r in recipients:
        get_object_or_404(RobogalsUser, pk=r['user'])
    msg['subject'] = message['subject']
    msg['html'] = message['body']
    msg_def_record = MessageDefinition(
        sender = sender_user,
        sender_role = sender_role,
        subject = msg['subject'],
        body = msg['html'],
        service = 1
    )
    if ('attachments' in message) and message['attachments']:
        attachments = []
        for a in message['attachments']:
            attach = {'name': a['name'], 'content': base64.b64encode(a['content'])}
            attachments.append(attach)
        msg['attachments'] = attachments
        msg_def_record.attachments = JSONRenderer().render(msg['attachments'])
    msg_def_record.save()
    to = []
    try_later = False
    msg_record_dict = {}
    recipients_per_req = 3
    retval = 1
    for rs in [recipients[i:i+recipients_per_req] for i in xrange(0, len(recipients), recipients_per_req)]:
        for r in rs:
            recipient_user = get_object_or_404(RobogalsUser, pk=r['user'])
            to_user = {'email': recipient_user.primary_email}
            if 'name' in r:
                to_user['name'] = r['name']
            else:
                to_user['name'] = recipient_user.get_full_name()
            to.append(to_user)
            msg_record = Message(
                definition = msg_def_record,
                recipient_user = recipient_user
            )
            msg_record.save()
            msg_record_dict[recipient_user.primary_email] = msg_record
        msg['to'] = to
        try:
            if try_later:
                raise Exception("try later")
            else:
                results = mandrill_client.messages.send(message=msg, async=False,
                             ip_pool='Main Pool')
        except Exception as e:
            try_later = True
            retval = 2
        else:
            for r in results:
                msg_record_dict[r['email']].service_id = r['_id']
                msg_record_dict[r['email']].service_status = r['status']
                msg_record_dict[r['email']].save()
        to = []
        msg_record_dict = {}
    return retval

def send_message(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        if data['type'] == 'email':
            retval = send_email(data['sender'], data['recipients'], data['message'])
        else:
            raise Http404
        return JSONResponse({'status': retval}, status=201)
    else:
        raise Http404
