from django.http import HttpResponse
from Servers.models import Server
from django.shortcuts import render

def home(request):
    servers = Server.objects.filter(checked__isnull=False, srv_ok=True)
    return render(request, 'index.html', {'servers': servers})