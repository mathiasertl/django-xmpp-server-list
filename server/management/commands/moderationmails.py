# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list).
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

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template import Context
from django.template import loader

from server.models import Server

User = get_user_model()


class Command(BaseCommand):
    help = 'Send an E-Mail to admins if a server needs moderation.'

    def handle(self, *args, **options):
        perm = Permission.objects.get(codename='moderate')
        query = Q(groups__permissions=perm) | Q(user_permissions=perm)
        users = User.objects.filter(query | Q(is_superuser=True)).distinct()
        protocol = getattr(settings, 'DEFAULT_PROTOCOL', 'https')
        domain = getattr(settings, 'DEFAULT_DOMAIN', 'list.jabber.at')

        servers = Server.objects.for_moderation()
        servers = servers.filter(moderators_notified=False)
        if servers.exists():
            return
        servers.update(moderators_notified=True)

        subject = '[%s] %s servers awaiting moderation' % (
            settings.SITENAME, len(servers)
        )

        t = loader.get_template('server/mail/moderationmail.html')
        for user in users:
            c = Context({
                'servers': servers,
                'user': user,
                'sitename': settings.SITENAME,
                'protocol': protocol,
                'domain': domain,
            })

            body = t.render(c)

            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email],
                      fail_silently=False)
