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
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.edit import UpdateView

from confirm.models import UserConfirmationKey
from core.views import AnonymousRequiredMixin
from server.util import get_siteinfo

from .forms import CreationForm
from .forms import PasswordChangeForm
from .forms import PasswordResetForm


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


class UpdateUserView(LoginRequiredMixin, UpdateView):
    fields = ['email', 'jid']
    success_url = reverse_lazy('account:index')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # set *_confirmed properties before calling super() so they are saved to the database
        if 'email' in form.changed_data:
            form.instance.email_confirmed = False
        if 'jid' in form.changed_data:
            form.instance.jid_confirmed = False

        response = super().form_valid(form)

        # TODO: this still uses the same template as when a user is created
        if 'email' in form.changed_data:
            UserConfirmationKey.objects.filter(subject=form.instance, type='E').delete()
            key = UserConfirmationKey.objects.create(subject=form.instance, type='E')
            key.send(*get_siteinfo(self.request))
        if 'jid' in form.changed_data:
            UserConfirmationKey.objects.filter(subject=form.instance, type='J').delete()
            key = UserConfirmationKey.objects.create(subject=form.instance, type='J')
            key.send(*get_siteinfo(self.request))

        return response


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


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('account:index')
    template_name = 'account/password_change_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Password was successfully updated.'))
        return response


class PasswordResetView(AnonymousRequiredMixin, auth_views.PasswordResetView):
    authenticated_url = reverse_lazy('account:index')
    form_class = PasswordResetForm
    template_name = 'account/password_reset_form.html'


class PasswordResetDoneView(AnonymousRequiredMixin, auth_views.PasswordResetDoneView):
    authenticated_url = reverse_lazy('account:index')
    template_name = 'account/password_reset_done.html'


class PasswordResetConfirmView(AnonymousRequiredMixin, auth_views.PasswordResetConfirmView):
    authenticated_url = reverse_lazy('account:index')
    template_name = 'account/password_reset_confirm.html'


class PasswordResetCompleteView(AnonymousRequiredMixin, auth_views.PasswordResetCompleteView):
    authenticated_url = reverse_lazy('account:index')
    template_name = 'account/password_reset_complete.html'
