from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from models import Server
from forms import ServerForm

@login_required
def index(request):
    forms = [ServerForm(instance=s, prefix=s.id) for s in request.user.servers.all()]
        
    return render(request, 'server/index.html', {'forms': forms, 'new_form': ServerForm()})

@permission_required('server.moderate')
def moderate(request):
    servers = Server.objects.filter(moderated=None)
    return render(request, 'server/moderate.html', {'servers': servers})

@login_required
def ajax(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            server = form.save(commit=False)
            server.user = request.user
            server.save()
            
            form = ServerForm(instance=server, prefix=server.id)
            return render(request, 'ajax/server_table_row.html', {'form': form})
            
        return HttpResponse(status=400)

@login_required
def ajax_id(request, server_id):
    server = Server.objects.get(id=server_id)
    if request.method == 'DELETE':
        if server.user != request.user:
            return HttpResponseForbidden("Thou shal only delete your own server!")
        
        server.delete()
    elif request.method == 'POST':
        form = ServerForm(request.POST, instance=server, prefix=server.id)
        if form.is_valid():
            if server.user != request.user:
                return HttpResponseForbidden("Thou shal only edit your own server!")
            form.save()
            form = ServerForm(instance=server, prefix=server.id)
        
        return render(request, 'ajax/server_table_row.html', {'form': form})
        
    return HttpResponse('ok.')
    
@permission_required('server.moderate')
def ajax_moderate(request):
    if request.method == 'POST':
        server_id = request.POST['id']
        server = Server.objects.get(id=server_id)
        if request.POST['moderate'] == 'true':
            server.moderated = True
        else:
            server.moderated = False
        server.save()
        return HttpResponse('ok')
    else:
        return HttpResponseForbidden('Sorry, only POST')