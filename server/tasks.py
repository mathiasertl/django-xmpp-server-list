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

import logging

from celery import shared_task

from confirm.models import ServerConfirmationKey

from .mails import send_moderation_mails
from .models import Server

log = logging.getLogger()


@shared_task
def remove_old_servers():
    Server.objects.dead().delete()


@shared_task
def send_contact_confirmation(server_pk, host, is_secure=True):
    server = Server.objects.get(pk=server_pk)

    ServerConfirmationKey.objects.filter(subject=server).delete()
    if server.contact_type == Server.CONTACT_TYPE_JID:
        typ = ServerConfirmationKey.TYPE_JID
    elif server.contact_type == Server.CONTACT_TYPE_EMAIL:
        typ = ServerConfirmationKey.TYPE_EMAIL
    else:
        log.error('%s: Server has unknown contact type: %s', server.domain, server.contact_type)
        return

    key = ServerConfirmationKey.objects.create(subject=server, type=typ)
    key.send('https' if is_secure else 'http', host)


@shared_task
def verify_server(domain):
    log.info('Verifying %s', domain)
    server = Server.objects.get(domain=domain)
    server.verify()


@shared_task
def verify_servers(*domains):
    if not domains:
        domains = Server.objects.values_list('domain', flat=True)

    for domain in domains:
        verify_server.delay(domain)


@shared_task
def moderation_mails():
    send_moderation_mails()
