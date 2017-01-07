from django.apps import AppConfig
from django.db.models.signals import pre_delete

def prevent_edit_delete(sender, instance, using, **kwargs):
	if hasattr(instance, 'username'):
		if getattr(instance, 'username') == 'edit':
			raise Exception("The 'edit' user cannot be deleted. It is a required system user in myRobogals.")

class RgProfileAppConfig(AppConfig):
	name = 'myrobogals.rgprofile'
	def ready(self):
		pre_delete.connect(prevent_edit_delete, dispatch_uid='delete_signal', weak=False)
