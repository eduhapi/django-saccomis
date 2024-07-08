from django import forms

class ComposeSMSForm(forms.Form):
    phone_number = forms.CharField(max_length=20)
    message = forms.CharField(widget=forms.Textarea)

