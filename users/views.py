#from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from models import ConfirmationKey, get_random_key
from forms import MyUserCreationForm

from xmpplist.Servers.forms import ServerForm

def index(request):
    servers = []
    for server in request.user.servers.all():
        form = ServerForm(instance=server)
        servers.append((server, form))
    return render(request, 'users/index.html', {'servers': servers})
    
def create(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # create user
            user = form.save()
            
            # create email confirmation:
            confirmation_key = ConfirmationKey.objects.create(user=user, key=get_random_key(user))
            confirmation_key.send(request)
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return redirect('users')
    else:
        form = MyUserCreationForm()
        
    return render(request, 'users/create.html', {'form': form})
    
@login_required
def confirm_email(request, key):
    try:
        key = ConfirmationKey.objects.get(key=key.lower())
    except ConfirmationKey.DoesNotExist:
        return render(request, 'users/confirm_email_error.html')
    
    if key.user != request.user:
        return render(request, 'users/confirm_email_error.html')
    
    request.user.profile.email_confirmed = True
    request.user.profile.save()
    key.delete()
    
    return redirect('users')

@login_required
def edit(request):
    return HttpResponse('edit')
    
@login_required
def set_password(request):
    return HttpResponse('set password')
    
def reset_password(request):
    return HttpResponse('<b>re</b>set password')