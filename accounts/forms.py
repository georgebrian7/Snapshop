from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
    Field('username', 
          css_class='form-control username-field', 
          placeholder='Choose a username',
          autocomplete='username'),
    Field('email', 
          css_class='form-control email-field', 
          placeholder='your.email@example.com',
          autocomplete='email'),
    Field('phone_number', 
          css_class='form-control phone-field', 
          placeholder='Phone number',
          autocomplete='tel'),
    Field('password1', 
          css_class='form-control password-field', 
          placeholder='Create password',
          autocomplete='new-password'),
    Field('password2', 
          css_class='form-control password-field', 
          placeholder='Confirm password',
          autocomplete='new-password')
        )
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number']
            )
        return user