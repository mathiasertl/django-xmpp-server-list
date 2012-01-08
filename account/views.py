from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from forms import MyUserCreationForm, UserPreferencesForm, UserPasswordForm, UserPasswordResetForm

from xmpplist.confirm.models import UserConfirmationKey, UserPasswordResetKey

@login_required
def index(request):
    return render(request, 'users/index.html')
    
def create(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # create user
            user = form.save()
            
            # create email confirmation:
            key = UserConfirmationKey.objects.create(user=user)
            key.send(request, typ='E') # send to email address (for now)
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return redirect('users')
    else:
        form = MyUserCreationForm()
        
    return render(request, 'users/create.html', {'form': form})

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
    if request.user.is_authenticated():
        return redirect('users_set_password')
    
    if request.method == 'POST':
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            
            # send reset-key:
            key = UserPasswordResetKey(user=user)
            key.save()
            key.send(request)
    else:
        form = UserPasswordResetForm()
        
    return render(request, 'users/reset_password.html', {'form': form})