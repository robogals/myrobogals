from myrobogals.auth.models import User, Group
from myrobogals.rgprofile.usermodels import University

class RgImportCsvException(Exception):
	def __init__(self, errmsg):
		self.errmsg = errmsg
	def __str__(self):
		return self.errmsg

def importcsv(filerows, welcomeemail, defaults):
	raise RgImportCsvException("error")
