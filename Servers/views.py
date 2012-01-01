from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden

from models import Server

@login_required
def ajax(request):
    pass

@login_required
def ajax_id(request, server_id):
    if request.method == 'DELETE':
        server = Server.objects.get(id=server_id)
        if server.user != request.user:
            return HttpResponseForbidden("Thou shal only delete your own server!")
        
        server.delete()
    elif request.method == 'POST':
        print('doing a post...')
    return HttpResponse('ok.')