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
from django.utils.translation import ugettext_lazy as _

from .forms import ServerAdminForm
from .models import Certificate
from .models import CertificateAuthority
from .models import Features
from .models import Server
from .models import ServerSoftware


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['serial', 'ca', 'valid', 'last_seen']


class ServerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [('domain', 'launched'), ('added', 'modified', ),
                       ('last_checked', 'last_seen', ), ('country', 'country_cc')],
        }),
        (_('Homepage'), {
            'fields': ['website', ('registration_url', 'policy_url', ), ],
        }),
        (_('Technical verification'), {
            'fields': [('c2s_srv_records', 's2s_srv_records'),
                       ('c2s_tls_verified', 's2s_tls_verified'),
                       ('c2s_starttls'),
                       ],
        }),
        (_('Contact'), {
            'fields': [('contact_type', 'contact'), 'contact_name', 'contact_verified'],
        }),
        (_('Moderation'), {
            'fields': ['moderated', 'moderators_notified', 'moderation_message'],
            'description': _('Fields concerning the manual moderation.')
        }),
    ]
    form = ServerAdminForm
    list_display = ('verified', 'moderated', 'domain', 'user', 'last_seen')
    list_display_links = ('domain', 'user', )
    readonly_fields = ['added', 'modified', 'last_checked', 'last_seen', 'country', 'country_cc']
    search_fields = ('domain', )

    class Media:
        css = {
            'all': (
                'core/admin/base.css',
                'admin/server.css',
            ),
        }

    def verified(self, obj):
        return obj.verified
    verified.boolean = True


admin.site.register(Server, ServerAdmin)
admin.site.register(ServerSoftware)
admin.site.register(Features)
admin.site.register(CertificateAuthority)
