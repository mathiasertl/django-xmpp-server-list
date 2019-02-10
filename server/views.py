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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from server.forms import CreateServerForm
from server.forms import UpdateServerForm
from server.models import Server


class MyServerMixin(LoginRequiredMixin):
    """Makes sure that a ModelView is only called with servers the user owns."""

    queryset = Server.objects.order_by('domain')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class MyServerFormMixin(MyServerMixin):
    """Set the form prefix to the servers id."""
    def get_prefix(self):
        return self.object.id


class IndexView(ListView):
    queryset = Server.objects.moderated().verified().order_by('domain')


class MyServerListView(MyServerMixin, ListView):
    template_name_suffix = '_list_user'


class ServerCreateView(LoginRequiredMixin, CreateView):
    model = Server
    form_class = CreateServerForm
    queryset = Server.objects.all()
    template_name_suffix = '_create'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ServerUpdateView(MyServerMixin, UpdateView):
    form_class = UpdateServerForm
    template_name_suffix = '_update'


class ServerDetailView(DetailView):
    queryset = Server.objects.all()


class ModerateView(PermissionRequiredMixin, ListView):
    permission_required = 'server.moderate'
    template_name = 'server/moderate.html'
    queryset = Server.objects.for_moderation()


class ReportView(MyServerMixin, DetailView):
    queryset = Server.objects.all()
    template_name = 'server/ajax/report.html'


class AjaxServerDeleteView(MyServerMixin, DeleteView):
    model = Server
    http_method_names = ('delete', )

    def delete(self, request, *args, **kwargs):
        """Omit success_url etc."""
        self.get_object().delete()
        return HttpResponse()


class AjaxServerResendView(MyServerMixin, SingleObjectMixin, View):
    queryset = Server.objects.filter(contact_verified=False)
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        server = self.get_object()
        server.do_contact_verification(request)
        return HttpResponse()


class AjaxServerModerateView(PermissionRequiredMixin, SingleObjectMixin, View):
    queryset = Server.objects.for_moderation()
    permission_required = 'server.moderate'
    http_method_names = ('post', )

    def post(self, request, *args, **kwargs):
        server = self.get_object()
        if request.POST['moderate'] == 'true':
            server.moderated = True
            server.moderation_message = ''
            server.contact_verified = True
        else:
            server.moderated = False
            server.moderation_message = request.POST['message']
        server.save()
        return HttpResponse()
