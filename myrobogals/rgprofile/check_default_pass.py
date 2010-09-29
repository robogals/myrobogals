# To use this script:
# python manage.py shell
# from myrobogals.rgprofile.check_default_pass import check_default_pass

from myrobogals.auth.models import check_password
from myrobogals.auth.models import User
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient

def check_default_pass():
	users = User.objects.all()
	for u in users:
		if check_password("newrg123", u.password):
			message = EmailMessage()
			message.body = "Dear " + u.first_name + ",\n\nYou are recieving this automated email because your myRobogals account is still set to use the default password. This is a security risk and exposes your myRobogals account to potentially being used by others.\n\nPlease login at http://my.robogals.org using the following credentials:\nUsername: " + u.username + "\nPassword: newrg123\n\nOnce you have logged in, please change your password.\n\nThankyou,\n\nmyRobogals password nagging bot :)"
			message.subject = "Warning: Account is using default password"
			message.from_address = "my@robogals.org"
			message.from_name = "myRobogals"
			message.reply_address = "my@robogals.org"
			message.html = False
			message.status = -1
			message.sender_id = 168
			message.save()
			recipient = EmailRecipient()
			recipient.message = message
			recipient.user = u
			recipient.to_name = u.get_full_name()
			recipient.to_address = u.email
			recipient.save()
			message.status = 0
			message.save()
