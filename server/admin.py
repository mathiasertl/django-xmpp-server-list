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
