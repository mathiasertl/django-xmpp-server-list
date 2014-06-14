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

from __future__ import unicode_literals, print_function

import gzip
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.six.moves.urllib.request import urlretrieve


class Command(BaseCommand):
    help = 'Download GeoIP database.'

    def handle(self, *args, **options):
        if not os.path.exists(settings.GEOIP_CONFIG_ROOT):
            os.makedirs(settings.GEOIP_CONFIG_ROOT)

        print("Downloading database... ", end='')
        compressed = '%s.gz' % settings.GEOIP_CITY_PATH
        urlretrieve('http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                    compressed)
        print("Done.")

        with open(settings.GEOIP_CITY_PATH, 'wb') as _out, gzip.open(compressed, 'rb') as _in:
            _out.write(_in.read())
        os.remove(compressed)
