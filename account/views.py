#from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from models import ConfirmationKey, get_random_key
from forms import MyUserCreationForm, UserPreferencesForm, UserPasswordForm

from xmpplist.server.forms import ServerForm

@login_required
def index(request):
    servers = []
    for server in request.user.servers.all():
        form = ServerForm(instance=server)
        servers.append((server, form))
        
    return render(request, 'users/index.html', {'servers': servers, 'new_form': ServerForm()})
    
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
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST, instance=request.user)
        
        if form.is_valid():
            user = form.save()
            
            if 'email' in form.changed_data:
                print('changed email!')
                user.profile.email_confirmed = False
                user.profile.save()
                
                # TODO: resend confirmation
    else:
        form = UserPreferencesForm(instance=request.user)
        
    return render(request, 'users/edit.html', {'form': form})
    
@login_required
def set_password(request):
    if request.method == 'POST':
        form = UserPasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
    else:        
        form = UserPasswordForm()
        
    return render(request, 'users/set_password.html', {'form': form})
    
def reset_password(request):
    return HttpResponse('<b>re</b>set password')