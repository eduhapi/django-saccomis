from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name','last_name', 'email', 'phone', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='username')

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label='Email', max_length=254)

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='New password confirmation', widget=forms.PasswordInput)
