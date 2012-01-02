from django.contrib import admin

from models import ServerReport, Server, CertificateAuthority, ServerSoftware

admin.site.register(Server)
admin.site.register(ServerSoftware)
admin.site.register(ServerReport)
admin.site.register(CertificateAuthority)