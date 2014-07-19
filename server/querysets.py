# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-list (https://list.jabber.at).
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

from __future__ import unicode_literals

from django.db.models import Q
from django.db.models.query import QuerySet

from server.constants import CONTACT_TYPES


class ServerQuerySet(QuerySet):
    def plain(self):
        """Servers that allow unencrypted connections."""
        return self.filter(c2s_starttls_required=False)

    def c2s_secure(self):
        """Servers that only allow encrypted c2s connections."""
        return self.exclude(c2s_starttls_required=True)

    def s2s_secure(self):
        """Servers that only allow encrypted s2s connections."""
        return self.exclude(s2s_starttls_required=True)

    def secure(self):
        """Servers that only allow encrypted c2s/s2s connections."""
        return self.c2s_secure().s2s_secure()

    def ssl(self):
        """Return servers that allow SSL connections."""
        return self.filter(ssl_port__isnull=False).filter(
            Q(c2s_ssl_verified=True) | Q(ca__certificate__isnull=True))

    def tls(self):
        """Return servers that allow TLS connections."""
        return self.filter(c2s_starttls=True).filter(
            Q(c2s_tls_verified=True) | Q(ca__certificate__isnull=True))

    def verified(self):
        qs = self.filter(
            c2s_srv_records=True, s2s_srv_records=True).filter(
            Q(c2s_ssl_verified=True) | Q(ca__certificate__isnull=True),
        ).tls()

        return qs

    def moderated(self):
        return self.filter(moderated=True, user__email_confirmed=True,
                           user__jid_confirmed=True)

    def for_moderation(self):
        """List all servers suitable for moderation.

        Lists servers that are unmoderated, have valid SRV records, a working SSL/TLS setup and are
        not yet moderated. It also excludes servers where the contact should be automatically
        verified but the user has failed to confirm this.
        """
        return self.verified().filter(moderated=None).exclude(
            (Q(contact_type=CONTACT_TYPES.JID) | Q(contact_type=CONTACT_TYPES.EMAIL))
            & Q(contact_verified=False))
