from django.contrib import admin

from models import CertificateAuthority
from models import Features
from models import LogEntry
from models import Server
from models import ServerSoftware


admin.site.register(Server)
admin.site.register(ServerSoftware)
admin.site.register(Features)
admin.site.register(CertificateAuthority)
admin.site.register(LogEntry)
