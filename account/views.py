from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from forms import CreationForm, PreferencesForm, ProfileForm, PasswordResetForm

from xmpplist.confirm.models import UserConfirmationKey, UserPasswordResetKey

@login_required
def index(request):
    return render(request, 'account/index.html')
    
def create(request):
    if request.method == 'POST':
        user_form = CreationForm(request.POST, prefix='user')
        profile_form = ProfileForm(request.POST, prefix='profile')
        if user_form.is_valid() and profile_form.is_valid():
            # create user
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            # create confirmations:
            ekey = UserConfirmationKey.objects.create(user=user, type='E')
            ekey.send(request)
            jkey = UserConfirmationKey.objects.create(user=user, type='J')
            jkey.send(request)
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return redirect('account')
    else:
        user_form = CreationForm(prefix='user')
        profile_form = ProfileForm(prefix='profile')
        
    return render(request, 'account/create.html',
                  {'user_form': user_form, 'profile_form': profile_form}
    )

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = PreferencesForm(request.POST, instance=request.user, prefix='user')
        profile_form = ProfileForm(request.POST, instance=request.user.profile, prefix='profile')
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save()
            
            if 'email' in user_form.changed_data:
                profile.email_confirmed = False
                profile.save()
                UserConfirmationKey.objects.filter(user=user, type='E').delete()
                key = UserConfirmationKey.objects.create(user=user, type='E')
                key.send(request)
            if 'jid' in profile_form.changed_data:
                profile.jid_confirmed = False
                profile.save()
                UserConfirmationKey.objects.filter(user=user, type='J').delete()
                key = UserConfirmationKey.objects.create(user=user, type='J')
                key.send(request)
                
            return redirect('account')
    else:
        user_form = PreferencesForm(instance=request.user, prefix='user')
        profile_form = ProfileForm(instance=request.user.profile, prefix='profile')
        
    return render(request, 'account/edit.html',
                  {'user_form': user_form, 'profile_form': profile_form}
    )
    
def reset_password(request):
    if request.user.is_authenticated():
        return redirect('account_set_password')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            
            # send reset-key:
            key = UserPasswordResetKey(user=user)
            key.save()
            key.send(request)
    else:
        form = PasswordResetForm()
        
    return render(request, 'account/reset_password.html', {'form': form})