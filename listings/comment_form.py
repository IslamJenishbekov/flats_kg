from django import forms
from .models import ListingComment


class CommentForm(forms.ModelForm):
    class Meta:
        model = ListingComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'w-full p-2 border rounded'}),
        }
