from django import forms
from .models import BookTest, Book
from django.forms.widgets import NumberInput
class ContactForm(forms.Form):
    name = forms.CharField(label='Name')
    email = forms.EmailField(label='E-mail')
    message = forms.CharField(label='Message', widget=forms.Textarea())


class CommentForm(forms.Form):
    text = forms.CharField(label='Add comment:', widget=forms.Textarea(
        attrs={'rows': 4, 'cols': 15}))

class Test(forms.ModelForm):
    file = forms.FileField()
    name = forms.CharField()
    class Meta:
        model = BookTest
        fields = ['file', 'name']

class BookForms(forms.ModelForm):
    publish_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
    class Meta:
        model = Book
        fields = ['file', 'title', 'description', 'image', 'author', 'book_amount', 'publish_date', 'number_of_pages', 'category']