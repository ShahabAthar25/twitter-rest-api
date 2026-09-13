from django import forms

from .models import *

class TweetCeationChangeForm(forms.ModelForm):
    
    class Meta:
        model = Tweet
        fields = ('content', 'quote_tweet')

class ReplyCreationForm(forms.ModelForm):
    
    class Meta:
        model = Reply
        fields = ('tweet', 'parent_reply', 'content')

class ReplyChangeForm(forms.ModelForm):
    
    class Meta:
        model = Reply
        fields = ('tweet', 'parent_reply', 'content', 'owner')
        widgets = {
            'owner': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
        

class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ('image', 'description')
        widgets = {
            'image': forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
        }