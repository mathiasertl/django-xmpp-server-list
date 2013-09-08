# -*- coding: utf-8 -*-
#
# This file is part of xmpplist (https://list.jabber.at).
#
# xmpplist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppllist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmpplist.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from xmpplist.confirm.models import UserConfirmationKey
from xmpplist.confirm.models import UserPasswordResetKey
from xmpplist.confirm.models import ServerConfirmationKey


def confirm_user_contact(request, key):
    if request.user.is_authenticated():
        key = get_object_or_404(UserConfirmationKey,
                                **{'key': key, 'user': request.user})
    else:
        key = get_object_or_404(UserConfirmationKey, **{'key': key})
        key.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, key.user)

    if key.type == 'E':
        key.user.email_confirmed = True
    elif key.type == 'J':
        key.user.jid_confirmed = True
    else:
        raise RuntimeError('Invalid confirmation key-type: %s' % key.type)
    key.user.save()

    # remove existing confirmation keys:
    UserConfirmationKey.objects.invalidate(subject=key.user)
    return redirect('account')


def reset_user_password(request, key):
    if request.user.is_authenticated():
        key = get_object_or_404(UserPasswordResetKey,
                                **{'key': key, 'user': request.user})
    else:
        key = get_object_or_404(UserPasswordResetKey, **{'key': key})
        key.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, key.user)

    # remove existing keys for this user:
    UserPasswordResetKey.objects.invalidate(subject=key.user)
    return redirect('account_set_password')


def confirm_server(request, key):
    key = get_object_or_404(ServerConfirmationKey, **{'key': key})
    key.server.contact_verified = True
    key.server.save()

    ServerConfirmationKey.objects.invalidate(subject=key.server)
    return redirect('server')
