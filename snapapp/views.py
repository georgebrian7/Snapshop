from django.shortcuts import render,redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
# from corona.analyzer import main
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from django.core.files.storage import default_storage
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
# Create your views here.
def index(request):
    return render(request,'index.html')

def camera(request):
    if request.method == 'POST':
        image_path = request.POST["src"]
        image = NamedTemporaryFile()
        urlopen(image_path).read()
        image.write(urlopen(image_path).read())
        image.flush()
        image = File(image)
        name = str(image.name).split('\\')[-1]
        name += '.jpg'  
        image.name = name
        with open('image.txt', 'w+') as file:
            file.write(str(name))
        default_storage.save('C:/Users/George Brian/repos/Snapshop/snapshop/media/a.jpg', ContentFile(urlopen(image_path).read()))
        return HttpResponse('Done!')
    return render(request, 'index.html')

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"