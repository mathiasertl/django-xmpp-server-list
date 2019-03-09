# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list).
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# django-xmpp-server-list is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import time

from django.core.management.base import BaseCommand

from server.models import Server

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verify servers'

    def add_arguments(self, parser):
        parser.add_argument('server', nargs='*', help='Verify only the given servers.')

    def handle(self, *args, **options):
        if options['server']:
            for domain in options['server']:
                try:
                    log.info('Verifying %s', domain)
                    Server.objects.get(domain=domain).verify()
                except Server.DoesNotExist:
                    log.error('Could not find %s', domain)
        else:
            # Cleanup old servers if we run without arguments
            Server.objects.dead().delete()

            for server in Server.objects.all().order_by('domain'):
                log.info('Verifying %s', server.domain)
                server.verify()

        time.sleep(2)
        os._exit(0)
