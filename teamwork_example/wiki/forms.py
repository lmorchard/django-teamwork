from django import forms

from teamwork_example.wiki.models import Document


class DocumentCreateForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'team', 'content',] 


class DocumentEditForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['content',] 
