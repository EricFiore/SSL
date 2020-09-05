from django import forms
from .models import Message


class CommunicationForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ['send_to', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'cols': 50, 'rows': 5})
        }
