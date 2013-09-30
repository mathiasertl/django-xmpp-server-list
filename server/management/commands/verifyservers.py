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

import logging
import os
import time

from datetime import datetime
from datetime import timedelta

from django.core.management.base import BaseCommand
from xmpplist.server.models import Server

class Command(BaseCommand):
    args = '[domain ...]'
    help = 'Verify servers'

    def handle(self, *args, **options):
        # some initial cleanup first:
        delta = datetime.today() - timedelta(days=14)
        Server.objects.filter(last_seen__lt=delta).delete()

        if args:
            for domain in args:
                try:
                    Server.objects.get(domain=domain).verify()
                except Server.DoesNotExist:
                    logging.error('Could not find %s', domain)
        else:
            for server in Server.objects.all().order_by('domain'):
                server.verify()

            time.sleep(2)
            os._exit(0)
