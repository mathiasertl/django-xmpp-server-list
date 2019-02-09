# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list)
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

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from account.forms import CreationForm
from account.forms import PasswordResetForm
from account.forms import PreferencesForm
from confirm.models import UserConfirmationKey
from confirm.models import UserPasswordResetKey
from server.util import get_siteinfo


@login_required
def index(request):
    return render(request, 'account/index.html')


def create(request):
    if request.method == 'POST':
        form = CreationForm(request.POST, prefix='user')
        if form.is_valid():
            # create user
            user = form.save()

            # create confirmations:
            ekey = UserConfirmationKey.objects.create(subject=user, type='E')
            ekey.send(*get_siteinfo(request))
            jkey = UserConfirmationKey.objects.create(subject=user, type='J')
            jkey.send(*get_siteinfo(request))

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            return redirect('account:indexfoo')
    else:
        form = CreationForm(prefix='user')

    return render(request, 'account/create.html', {'user_form': form, })


@login_required
def edit(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save()

            if 'email' in form.changed_data:
                user.email_confirmed = False
                user.save()
                UserConfirmationKey.objects.filter(
                    subject=user, type='E').delete()
                key = UserConfirmationKey.objects.create(subject=user, type='E')
                key.send(*get_siteinfo(request))
            if 'jid' in form.changed_data:
                user.jid_confirmed = False
                user.save()
                UserConfirmationKey.objects.filter(
                    subject=user, type='J').delete()
                key = UserConfirmationKey.objects.create(subject=user, type='J')
                key.send(*get_siteinfo(request))

            return redirect('account')
    else:
        form = PreferencesForm(instance=request.user)

    return render(request, 'account/edit.html', {'user_form': form, })


class ResetPassword(FormView):
    template_name = 'account/reset_password.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('account:reset_password_ok')

    def dispatch(self, request, *args, **kwargs):
        # TODO: view is unused but this trick should be used in django view
        if request.user.is_authenticated:
            return redirect('account:set_password')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        key = UserPasswordResetKey.objects.create(subject=form.user)
        key.send(*get_siteinfo(self.request))

        return super(ResetPassword, self).form_valid(form)


@login_required
def resend_confirmation(request):
    if not request.user.email_confirmed:
        key = UserConfirmationKey.objects.create(subject=request.user, type='E')
        key.send(*get_siteinfo(request))
    if not request.user.jid_confirmed:
        key = UserConfirmationKey.objects.create(subject=request.user, type='J')
        key.send(*get_siteinfo(request))
    return render(request, 'account/resend_confirmation.html',
                  {'jid': settings.XMPP['default']['jid']})
