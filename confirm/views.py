# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-list (https://list.jabber.at).
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify
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
# along with django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic.base import RedirectView
from django.views.generic.detail import SingleObjectMixin

from confirm.models import UserConfirmationKey
from confirm.models import UserPasswordResetKey
from confirm.models import ServerConfirmationKey


class ConfirmationView(RedirectView, SingleObjectMixin):
    # from SingleObjectMixin
    pk_url_kwarg = 'key'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(key=self.kwargs['key'])
        except self.model.DoesNotExist:
            raise Http404

    def get_redirect_url(self, *args, **kwargs):
        queryset = self.get_queryset().for_user(user=self.request.user)

        # get confirmation key:
        key = self.get_object(queryset=queryset.valid())

        if not self.request.user.is_authenticated():
            key.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(self.request, key.user)

        # log user in if not authenticated so far:
        if not self.request.user.is_authenticated():
            key.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(self.request, key.user)

        # take any confirmation action
        key.confirm()

        # invalidate old keys/unused keys:
        queryset.invalidate(subject=key.user)  # delete all old ones for this user
        self.get_queryset().invalidate_outdated()  # delete expired keys

        return reverse(self.url)


class UserConfirmationView(ConfirmationView):
    model = UserConfirmationKey
    url = 'account'


class ResetUserPasswordView(ConfirmationView):
    model = UserPasswordResetKey
    url = 'account_set_password'


class ConfirmServerContactView(ConfirmationView):
    model = ServerConfirmationKey
    url = 'server'
