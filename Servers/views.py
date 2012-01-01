from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden

from models import Server
from forms import ServerForm

@login_required
def ajax(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            server = form.save(commit=False)
            server.user = request.user
            server.save()
            return HttpResponse('ok.')
            
        print(form)
        return HttpResponseForbidden('error')

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
                return HttpResponseForbidden("Thou shal only delete your own server!")
            form.save()
            return HttpResponse('ok')
        
        return HttpResponseForbidden('error')
        
    return HttpResponse('ok.')