from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from models import Server
from forms import ServerForm

@login_required
def index(request):
    servers = []
    for server in request.user.servers.all():
        form = ServerForm(instance=server)
        servers.append((server, form))
        
    return render(request, 'server/index.html', {'servers': servers, 'new_form': ServerForm()})

@permission_required('server.moderate')
def moderate(request):
    servers = Server.objects.filter(moderated=False)
    return render(request, 'server/moderate.html', {'servers': servers})

@login_required
def ajax(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            server = form.save(commit=False)
            server.user = request.user
            server.save()
            
            new_form = ServerForm(instance=server)
            return render(request, 'ajax/server_table_row.html', {'server': server, 'form': form})
            
        return HttpResponse(status=400)

@login_required
def ajax_id(request, server_id):
    server = Server.objects.get(id=server_id)
    if request.method == 'DELETE':
        if server.user != request.user:
            return HttpResponseForbidden("Thou shal only delete your own server!")
        
        server.delete()
    elif request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            if server.user != request.user:
                return HttpResponseForbidden("Thou shal only edit your own server!")
            form.save()
        
        return render(request, 'ajax/server_table_row.html', {'server': server, 'form': form})
        
    return HttpResponse('ok.')