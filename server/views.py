from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render

from xmpplist.server.forms import ServerForm
from xmpplist.server.forms import ServerLocationForm
from xmpplist.server.models import Features
from xmpplist.server.models import Server


@login_required
def index(request):
    servers = request.user.servers.all()
    forms = [ServerForm(instance=s, prefix=s.id,
                        initial={
                            'location': '%s,%s' % (s.location.x, s.location.y)
                        })
        for s in servers]
    context = {
        'forms': forms,
        'new_server_form': ServerForm(),
        'location_form': ServerLocationForm(),  # preload location-form media
    }
    return render(request, 'server/index.html', context)


@permission_required('server.moderate')
def moderate(request):
    servers = Server.objects.filter(moderated=None)
    return render(request, 'server/moderate.html', {'servers': servers})


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
                instance=server, prefix=server.id, initial={
                    'location': '%s,%s' % (
                        server.location.x, server.location.y),
                })
            return render(request, 'ajax/server_table_row.html',
                          {'form': form})
        return render(request, 'ajax/server_table_row.html',
                      {'form': form}, status=400)
    return HttpResponseForbidden("No humans allowed.")


@login_required
def ajax_mapbrowse(request):
    form = ServerLocationForm()
    return render(request, 'ajax/mapbrowse.html', {'form': form})


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
                instance=server, prefix=server.id, initial={
                    'location': '%s,%s' % (server.location.x,
                                           server.location.y)
                }
            )

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


@login_required
def ajax_id_mapbrowse(request, server_id):
    server = Server.objects.get(id=server_id)
    if server.user != request.user:
        return HttpResponseForbidden(
            "Thou shal only osmbrowse your own server!")

    form = ServerLocationForm(initial={'osmlocation': server.location},
                              prefix=server.id)
    maplocation = 'map_%s_osmlocation' % server.id
    return render(request, 'ajax/mapbrowse.html',
                  {'form': form, 'maplocation': maplocation})
