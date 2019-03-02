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
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from server.forms import CreateServerForm
from server.forms import UpdateServerForm
from server.models import Server


class MyServerMixin(LoginRequiredMixin):
    """Makes sure that a ModelView is only called with servers the user owns."""

    queryset = Server.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class IndexView(ListView):
    queryset = Server.objects.moderated().verified().order_by('domain')


class MyServerListView(MyServerMixin, ListView):
    queryset = Server.objects.order_by('domain')
    template_name_suffix = '_list_user'


class ServerCreateView(LoginRequiredMixin, CreateView):
    form_class = CreateServerForm
    model = Server
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
    queryset = Server.objects.order_by('domain').for_moderation()
    template_name = 'server/server_list_moderate.html'


class AjaxServerModerateView(PermissionRequiredMixin, SingleObjectMixin, View):
    http_method_names = ('post', )
    permission_required = 'server.moderate'
    queryset = Server.objects.for_moderation()

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
