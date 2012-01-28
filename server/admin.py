#from django.contrib import admin
from django.contrib.gis import admin

from models import Server, CertificateAuthority, ServerSoftware, Features, LogEntry

admin.site.register(Server, admin.OSMGeoAdmin)
admin.site.register(ServerSoftware)
admin.site.register(Features)
admin.site.register(CertificateAuthority)
admin.site.register(LogEntry)