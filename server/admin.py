# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list)
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppllist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import admin

from .models import CertificateAuthority
from .models import Features
from .models import Server
from .models import ServerSoftware


class ServerAdmin(admin.ModelAdmin):
    list_display = ('verified', 'moderated', 'domain', 'user', )
    list_display_links = ('domain', 'user', )
    search_fields = ('domain', )

    class Media:
        css = {
            'all': ('admin/server.css', ),
        }

    def verified(self, obj):
        return obj.verified
    verified.boolean = True


admin.site.register(Server, ServerAdmin)
admin.site.register(ServerSoftware)
admin.site.register(Features)
admin.site.register(CertificateAuthority)
