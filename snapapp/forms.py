from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import CustomUser


class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    phone_number = forms.CharField(max_length=15, required=False, help_text="Optional. Enter your phone number.")
    
    class Meta:
        model = CustomUser  
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')
    
    def save(self, commit=True):
        CustomUser = super().save(commit=False)
        CustomUser.email = self.cleaned_data['email']
        if hasattr(CustomUser, 'phone_number'):
            CustomUser.phone_number = self.cleaned_data['phone_number']
        if commit:
            CustomUser.save()
        return CustomUser