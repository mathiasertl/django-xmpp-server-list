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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views.generic import TemplateView

from xmpplist.server.forms import ServerForm
from xmpplist.server.models import Features
from xmpplist.server.models import Server


class IndexView(TemplateView):
    template_name = 'server/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        servers = self.request.user.servers.all()
        forms = [ServerForm(instance=s, prefix=s.id) for s in servers]

        context['new_server_form'] = ServerForm()
        context['forms'] = forms

        return context


class ModerateView(TemplateView):
    template_name = 'server/moderate.html'

    def get_context_data(self, **kwargs):
        context = super(ModerateView, self).get_context_data(**kwargs)
        context['servers'] = Server.objects.filter(moderated=None)

        return context


@login_required
def report(request, server_id):
    server = Server.objects.get(id=server_id)
    if server.user != request.user:
        return HttpResponseForbidden(
            "Thou shal only view reports of your own servers!")

    return render(request, 'server/report.html', {'server': server})


@login_required
def ajax(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            server = form.save(commit=False)
            server.user = request.user
            server.features = Features.objects.create()
            server.save()

            server.do_contact_verification()
            server.save()

            form = ServerForm(
                instance=server, prefix=server.id)
            return render(request, 'ajax/server_table_row.html',
                          {'form': form})
        return render(request, 'ajax/server_table_row.html',
                      {'form': form}, status=400)
    return HttpResponseForbidden("No humans allowed.")


@login_required
def ajax_id(request, server_id):
    server = Server.objects.get(id=server_id)
    if request.method == 'DELETE':
        if server.user != request.user:
            return HttpResponseForbidden(
                "Thou shal only delete your own server!")

        server.delete()
    elif request.method == 'POST':
        form = ServerForm(request.POST, instance=server, prefix=server.id)
        if form.is_valid():
            if server.user != request.user:
                return HttpResponseForbidden(
                    "Thou shal only edit your own server!")
            server = form.save()

            changed = set(form.changed_data)
            moderate_properties = {
                'contact',
                'contact_name',
                'contact_type',
                'website',
            }
            if 'domain' in changed:
                server.moderated = None
                server.verified = None
            if moderate_properties & changed:
                server.moderated = None
            if set(['ca', 'ssl_port']) & changed:
                server.verified = None

            # We have special treatment if contact was JID or email:
            if form.contact_changed():
                server.confirmations.all().delete()
                server.do_contact_verification()

            server.save()

            form = ServerForm(
                instance=server, prefix=server.id)

        return render(request, 'ajax/server_table_row.html', {'form': form})

    return HttpResponse('ok.')


@permission_required('server.moderate')
def ajax_moderate(request):
    if request.method == 'POST':
        server_id = request.POST['id']
        server = Server.objects.get(id=server_id)
        if request.POST['moderate'] == 'true':
            server.moderated = True
            server.contact_verified = True
        else:
            server.moderated = False
        server.save()
        return HttpResponse('ok')
    else:
        return HttpResponseForbidden('Sorry, only POST')
