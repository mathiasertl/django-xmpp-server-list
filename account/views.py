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
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView

from confirm.models import UserConfirmationKey
from core.views import AnonymousRequiredMixin
from server.util import get_siteinfo

from .forms import UserCreationForm
from .forms import PasswordChangeForm
from .forms import PasswordResetForm

UserModel = get_user_model()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'account/index.html'


class CreateUserView(AnonymousRequiredMixin, CreateView):
    form_class = UserCreationForm
    model = UserModel
    success_url = reverse_lazy('account:index')
    template_name_suffix = '_create'

    def form_valid(self, form):
        resp = super().form_valid(form)

        # create confirmations:
        ekey = UserConfirmationKey.objects.create(subject=self.object, type='E')
        ekey.send(*get_siteinfo(self.request))
        jkey = UserConfirmationKey.objects.create(subject=self.object, type='J')
        jkey.send(*get_siteinfo(self.request))

        # Finally, log the user in
        self.object.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, self.object)

        return resp


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
