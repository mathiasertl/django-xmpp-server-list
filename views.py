from server.models import Server
from django.shortcuts import render

def home(request):
    servers = Server.objects.filter(verified=True, moderated=True,
        user__profile__email_confirmed=True, user__profile__jid_confirmed=True).order_by('domain')

    return render(request, 'index.html', {'servers': servers})
