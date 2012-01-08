# Create your views here.
from django.contrib.auth import login
from django.shortcuts import redirect, get_object_or_404

from xmpplist.confirm.models import UserConfirmationKey, UserPasswordResetKey, ServerConfirmationKey

def confirm_user_contact(request, key):
    if request.user.is_authenticated():
        key = get_object_or_404(UserConfirmationKey, **{'key': key, 'user': request.user})
    else:
        key = get_object_or_404(UserConfirmationKey, **{'key': key})
        key.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, key.user)
    
    if key.type == 'E':
        key.user.profile.confirm_email = True
    elif key.type == 'J':
        key.user.profile.confirm_jid = True
    key.user.profile.save()
    
    # remove existing confirmation keys:
    UserConfirmationKey.objects.filter(user=key.user, type=key.type).delete()
    return redirect('account')

def reset_user_password(request, key):
    if request.user.is_authenticated():
        key = get_object_or_404(UserPasswordResetKey, **{'key': key, 'user': request.user})
    else:
        key = get_object_or_404(UserPasswordResetKey, **{'key': key})
        key.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, key.user)
    
    # remove existing keys for this user:
    UserPasswordResetKey.objects.filter(user=key.user).delete()
    return redirect('account_set_password')

def confirm_server(request, key):
    pass
