from django import forms
from .models import CustomFixComments, TechTipComment, ManualFixComment


class CustomFixCommentForm(forms.ModelForm):

    class Meta:
        model = CustomFixComments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 100, 'rows': 2})
        }


class TechTipCommentForm(forms.ModelForm):

    class Meta:
        model = TechTipComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 100, 'rows': 2})
        }


class ManualFixCommentForm(forms.ModelForm):

    class Meta:
        model = ManualFixComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 100, 'rows': 2})
        }