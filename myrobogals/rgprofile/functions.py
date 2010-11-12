from myrobogals.auth.models import User, Group
from myrobogals.rgprofile.usermodels import University
from datetime import datetime, date
import re

class RgImportCsvException(Exception):
	def __init__(self, errmsg):
		self.errmsg = errmsg
	def __str__(self):
		return self.errmsg

def stringval(colname, cell, newuser, defaults):
	data = cell.strip()
	if data != "":
		newuser.setattr(colname, data)
	else:
		if colname in defaults:
			newuser.setattr(colname, defaults[colname])

def dateval(colname, cell, newuser, defaults):
	data = cell.strip()
	try:
		date = datetime.strptime(data)
		newuser.setattr(colname, date)
	except ValueError:
		if colname in defaults:
			newuser.setattr(colname, defaults[colname])

def numval(colname, cell, newuser, defaults, options):
	data = cell.strip()
	try:
		num = int(data)
		if num in options:
			newuser.setattr(colname, num)
		else:
			raise ValueError
	except ValueError:
		if colname in defaults:
			newuser.setattr(colname, defaults[colname])

def boolval(colname, cell, newuser, defaults):
	data = cell.strip().lower()
	if data != "":
		if data == 'true':
			newuser.setattr(colname, True)
		elif data == '1':
			newuser.setattr(colname, True)
		elif data == 'yes':
			newuser.setattr(colname, True)
		else:
			if colname in defaults:
				newuser.setattr(colname, defaults[colname])
	else:
		if colname in defaults:
			newuser.setattr(colname, defaults[colname])

def check_username(username):
	try:
		User.objects.get(username=username)
	except User.DoesNotExist:
		return True
	return False

def generate_unique_username(row, columns):
	first_name = row[columns.index('first_name')]
	last_name = row[columns.index('last_name')]
	email = row[columns.index('email')]
	
	first_name_stripped = re.sub(r'\W+', '', first_name)
	last_name_stripped = re.sub(r'\W+', '', last_name)
	email_stripped = re.sub(r'\W+', '', fst(email.partition('@')))
	
	# Try different usernames until we find a unique one
	
	# Example: mark
	uname = (first_name_stripped)[0:30]
	if (check_username(uname)): return uname

	# Example: mparncutt
	uname = (first_name_stripped[0] + last_name_stripped)[0:30]
	if (check_username(uname)): return uname

	# Example: markp
	uname = (first_name_stripped + last_name_stripped[0])[0:30]
	if (check_username(uname)): return uname

	# Example: mp
	uname = (first_name_stripped[0] + last_name_stripped[0])[0:30]
	if (check_username(uname)): return uname

	# Example: parncutt
	uname = (last_name_stripped)[0:30]
	if (check_username(uname)): return uname

	# Example: markamon25
	uname = (email_stripped)[0:30]
	if (check_username(uname)): return uname

	# Example: markparncutt
	uname = (first_name_stripped + last_name_stripped)[0:30]
	if (check_username(uname)): return uname

	# Example: maparncutt
	uname = (first_name_stripped[0:2] + last_name_stripped)[0:30]
	if (check_username(uname)): return uname

	# Example: marparncutt
	uname = (first_name_stripped[0:3] + last_name_stripped)[0:30]
	if (check_username(uname)): return uname

	# Example: mparncutt2
	for i in range(1, 999):
		uname = (first_name_stripped[0] + last_name_stripped)[0:27] + str(i)
		if (check_username(uname)): return uname
	
	# Should never reach here, since the last case is pretty far-reaching
	raise RgImportCsvException('Could not generate unique username')

def importcsv(filerows, welcomeemail, defaults, chapter):
	columns = None
	for row in filerows:
		# Get column names from first row
		if (columns == None):
			columns = row
			if 'first_name' not in columns:
				raise RgImportCsvException('You must specify a first_name field')
			if 'last_name' not in columns:
				raise RgImportCsvException('You must specify a last_name field')
			if 'email' not in columns:
				raise RgImportCsvException('You must specify a email field')
			continue
		
		# Create new user
		newuser = User()
		
		# Process row
		i = 0;
		for cell in row:
			colname = columns[i]
			if colname == 'first_name':
				stringval(colname, cell, newuser, defaults)
			elif colname == 'last_name':
				stringval(colname, cell, newuser, defaults)
			elif colname == 'email':
				stringval(colname, cell, newuser, defaults)
			elif colname == 'username':
				data = cell.strip()
				if data != "":
					new_username = data
				else:
					new_username = generate_unique_username(row, columns)
				newuser.username = new_username
			elif colname == 'password':
				data = cell.strip()
				if data != "":
					plaintext_password = data
				else:
					plaintext_password = User.objects.make_random_password(6)
				newuser.set_password(plaintext_password)
			elif colname == 'alt_email':
				stringval(colname, cell, newuser, defaults)
			elif colname == 'mobile':
				num = cell.strip().replace(' ','').replace('+','')
				if num != '':
					regexes = MobileRegex.objects.filter(collection=chapter.mobile_regexes)
					try:
						number_valid = False
						for regex in regexes:
							matches = re.compile(regex.regex).findall(num)
							if matches == []:
								matches = re.compile(regex.regex).findall("0" + num)
								if matches == []:
									continue
								else:
									num = "0" + num
							num = regex.prepend_digits + num[regex.strip_digits:]
							number_valid = True
					except ValueError:
						number_valid = False
					if number_valid:
						newuser.mobile = num
			elif colname == 'date_joined':
				dateval(colname, cell, newuser, defaults)
			elif colname == 'dob':
				dateval(colname, cell, newuser, defaults)
			elif colname == 'gender':
				numval(colname, cell, newuser, defaults, range(0, 2))
			elif colname == 'course':
				stringval(colname, cell, newuser, defaults)
			elif colname == 'uni_start':
				dateval(colname, cell, newuser, defaults)
			elif colname == 'uni_end':
				dateval(colname, cell, newuser, defaults)
			elif colname == 'university_id':
				unis = University.objects.all()
				uni_ids = [-1]
				for uni in unis:
					uni_ids.append(uni.pk)
				numval(colname, cell, newuser, defaults, uni_ids)
				if newuser.getattr('university_id', 0) == -1:
					newuser.university_id = chapter.university_id
			elif colname == 'course_type':
				numval(colname, cell, newuser, defaults, range(1, 2))
			elif colname == 'student_type':
				numval(colname, cell, newuser, defaults, range(1, 2))
			elif colname == 'student_number':
				stringval(colname, cell, newuser, defaults)
			elif colname == 'privacy':
				numval(colname, cell, newuser, defaults, [0, 5, 10, 20])
			elif colname == 'dob_public':
				boolval(colname, cell, newuser, defaults)
			elif colname == 'email_public':
				boolval(colname, cell, newuser, defaults)
			elif colname == 'email_chapter_optin':
				boolval(colname, cell, newuser, defaults)
			elif colname == 'mobile_marketing_optin':
				boolval(colname, cell, newuser, defaults)
			elif colname == 'email_reminder_optin':
				boolval(colname, cell, newuser, defaults)
			elif colname == 'mobile_reminder_optin':
				boolval(colname, cell, newuser, defaults)
			elif colname == 'email_newsletter_optin':
				boolval(colname, cell, newuser, defaults)
			# Increment column and do the loop again
			i += 1

		# Should be the default at the model-level,
		# but just to be sure...
		newuser.is_active = True
		newuser.is_staff = False
		newuser.is_superuser = False

		# If we still don't have a username and/or password
		# by this stage, let's generate one
		if newuser.getattr('username', '') == '':
			new_username = generate_unique_username(row, columns)
			newuser.username = new_username
		if newuser.getattr('password', '') == '':
			plaintext_password = User.objects.make_random_password(6)
			newuser.set_password(plaintext_password)
			
		# Apply any unapplied defaults
		for key, value in defaults:
			if newuser.getattr(key, '') == '':
				newuser.setattr(key, value)

		# and finally...
		newuser.save()
		
		# Send welcome email
		message = EmailMessage()
		message.subject = welcomeemail['subject']
		try:
			message.body = welcomeemail['body'].format(
				chapter=chapter,
				user=user)
		except Exception:
			newuser.delete()
			raise RgImportCsvException('Welcome email format is invalid')
		message.from_address = 'my@robogals.org'
		message.reply_address = 'my@robogals.org'
		message.from_name = chapter.name
		message.sender = User.objects.get(username='edit')
		message.html = welcomeemail['html']
		message.status = -1
		message.save()
		recipient = EmailRecipient()
		recipient.message = message
		recipient.user = newuser
		recipient.to_name = newuser.get_full_name()
		recipient.to_address = newuser.email
		recipient.save()
		message.status = 0
		message.save()
