from django import forms
from .models import RepoContainer

class UploadFileForm(forms.Form):
    name = forms.CharField()
    file = forms.FileField()
    container = forms.ModelMultipleChoiceField(queryset=RepoContainer.objects.all())
    

