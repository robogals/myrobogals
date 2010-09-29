from myrobogals.auth.models import check_password
from myrobogals.auth.models import User

def check_default_pass():
	users = User.objects.all()
	for u in users:
		if check_password("newrg123", u.password):
			print "User " + u.username + " is using default password"
