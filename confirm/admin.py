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

from models import UserConfirmationKey
from models import UserPasswordResetKey
from models import ServerConfirmationKey


class UserConfirmationKeyAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created', 'type']
    list_filter = ['type']
    ordering = ['created']


class UserPasswordKeyAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created', 'type']
    list_filter = ['type']
    ordering = ['created']


class ServerConfirmationKeyAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created', 'type']
    list_filter = ['type']
    ordering = ['created']


admin.site.register(UserConfirmationKey, UserConfirmationKeyAdmin)
admin.site.register(UserPasswordResetKey, UserPasswordKeyAdmin)
admin.site.register(ServerConfirmationKey, ServerConfirmationKeyAdmin)
