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

from .models import Server

log = logging.getLogger()


@shared_task
def remove_old_servers():
    Server.objects.dead().delete()


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
