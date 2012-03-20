from django.db import models
from myrobogals.auth.models import Group

class Website(models.Model):
	site_name = models.CharField(max_length=64)
	site_url = models.CharField(max_length=64)
	site_chapter = models.ForeignKey(Group)
	ftp_host = models.CharField(max_length=64, blank=True)
	ftp_user = models.CharField(max_length=64, blank=True)
	ftp_pass = models.CharField(max_length=64, blank=True)
	ftp_path = models.CharField(max_length=64, blank=True)
	sql_host_int = models.CharField(max_length=64, blank=True)
	sql_host_ext = models.CharField(max_length=64, blank=True)
	sql_user = models.CharField(max_length=64, blank=True)
	sql_pass = models.CharField(max_length=64, blank=True)
	sql_dbname = models.CharField(max_length=64, blank=True)
	joomla_admin_url = models.CharField(max_length=64, blank=True)
	joomla_user = models.CharField(max_length=64, blank=True)
	joomla_pass = models.CharField(max_length=64, blank=True)
