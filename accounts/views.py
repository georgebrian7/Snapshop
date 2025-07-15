from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login
from .forms import CustomSignupForm

class SignUpView(CreateView):
    form_class = CustomSignupForm  # Changed from UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Auto-login user after successful signup
        login(self.request, self.object)
        return response