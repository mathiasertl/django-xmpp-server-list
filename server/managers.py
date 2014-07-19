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

from django.db import models

from server.querysets import ServerQuerySet


class ServerManager(models.Manager):
    def get_query_set(self):
        return ServerQuerySet(self.model)

    def plain(self):
        return self.get_query_set().plain()

    def c2s_secure(self):
        return self.get_query_set().c2s_secure()

    def s2s_secure(self):
        return self.get_query_set().s2s_secure()

    def secure(self):
        return self.get_query_set().secure()

    def ssl(self):
        return self.get_query_set().ssl()

    def tls(self):
        return self.get_query_set().tls()

    def verified(self):
        return self.get_query_set().verified()

    def moderated(self):
        return self.get_query_set().moderated()

    def for_moderation(self):
        return self.get_query_set().for_moderation()
