# -*- coding: utf-8 -*-
#
# This file is part of xmpplist (https://list.jabber.at).
#
# xmpplist is free software: you can redistribute it and/or modify
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
# along with xmpplist.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.db import models

from server.querysets import ServerQuerySet


class ServerManager(models.Manager):
    def get_query_set(self):
        return ServerQuerySet(self.model)

    def plain(self):
        return self.get_queryset().plain()

    def c2s_secure(self):
        return self.get_queryset().c2s_secure()

    def s2s_secure(self):
        return self.get_queryset().s2s_secure()

    def secure(self):
        return self.get_queryset().secure()

    def ssl(self):
        return self.get_queryset().ssl()

    def tls(self):
        return self.get_queryset().tls()
