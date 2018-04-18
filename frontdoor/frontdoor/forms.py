from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from frontdoor.choices import *

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, help_text='Required.')
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, help_text='Are you a Tenant or Landlord?')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type', )