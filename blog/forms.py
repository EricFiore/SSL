from django import forms
from django_summernote.widgets import SummernoteInplaceWidget, SummernoteWidget
from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'article_image']
        widgets = {
            'content': SummernoteWidget(),
        }