from django.contrib import admin

from models import Report, Server, CertificateAuthority, ServerSoftware

admin.site.register(Report)
admin.site.register(Server)
admin.site.register(ServerSoftware)
admin.site.register(CertificateAuthority)