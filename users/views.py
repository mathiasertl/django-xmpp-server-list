#from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login

from forms import MyUserCreationForm

def index(request):
    return render(request, 'users/index.html')
    
def create(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # create user
            user = form.save()
            
            # login user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return redirect('users')
    else:
        form = MyUserCreationForm()
        
    return render(request, 'users/create.html', {'form': form})
    
def edit(request):
    return HttpResponse('edit')
    
def set_password(request):
    return HttpResponse('set password')
    
def reset_password(request):
    return HttpResponse('<b>re</b>set password')