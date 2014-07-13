from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models.fields import FieldDoesNotExist
from django.db import transaction

from .models import EmailDefinition, EmailMessage
from .serializers import RobogalsUserSerializer

from django.conf import settings

import mandrill

class SendMessage(APIView):    
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(SendMessage, self).metadata(request)
        data.pop('description')
        return data
        
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_messages = list(request.DATA.get("message"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)

            
            
            
            
            
            
            
            
            
            
            
        try:
            mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
            message = {
                        'auto_html': False,
                        'auto_text': True,
                        
                        'from_email': 'message.from_email@example.com',
                        'from_name': 'Example Name',
                        
                        'to':   [
                                    {
                                        'email': 'recipient.email@example.com',
                                        'name': 'Recipient Name',
                                        'type': 'to'
                                    }
                                ],
                        'subject': 'example subject',
                        
                        'text': 'Example text content',
                        'html': '<p>Example HTML content</p>',
                        'inline_css': True,
                        
                        'preserve_recipients': False,
                        
                        'track_clicks': True,
                        'track_opens': True,
                      }
            result = mandrill_client.messages.send(message=message, async=False)

        except mandrill.Error, e:
            # Mandrill errors are thrown as exceptions
            print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
            # A mandrill error occurred: <class 'mandrill.UnknownSubaccountError'> - No subaccount exists with the id 'customer-123'    
            raise