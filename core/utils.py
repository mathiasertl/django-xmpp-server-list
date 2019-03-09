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

import gzip
import logging
import os

from django.conf import settings
from django.utils.six.moves.urllib.request import urlretrieve

log = logging.getLogger(__name__)


def add_colons(s):
    """Add colons after every second digit.

    This function is used in functions to prettify serials.

    >>> add_colons('teststring')
    'te:st:st:ri:ng'
    """
    return ':'.join([s[i:i + 2] for i in range(0, len(s), 2)])


def int_to_hex(i):
    """Create a hex-representation of the given serial.

    >>> int_to_hex(12345678)
    'BC:61:4E'
    """
    s = hex(i)[2:].upper()
    return add_colons(s)


def refresh_geoip_database():
    if not os.path.exists(settings.GEOIP_CONFIG_ROOT):
        os.makedirs(settings.GEOIP_CONFIG_ROOT)

    log.info("Downloading IPv4 database... ")
    compressed = '%s.gz' % settings.GEOIP_CITY_PATH
    urlretrieve('http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                compressed)

    with open(settings.GEOIP_CITY_PATH, 'wb') as _out, gzip.open(compressed, 'rb') as _in:
        _out.write(_in.read())
    os.remove(compressed)

    log.info("Downloading IPv6 database... ")
    compressed = '%s.gz' % settings.GEOIP_CITY_V6_PATH
    urlretrieve(
        'http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz',
        compressed)
    with open(settings.GEOIP_CITY_V6_PATH, 'wb') as _out, gzip.open(compressed, 'rb') as _in:
        _out.write(_in.read())
    os.remove(compressed)

    log.info("Done downloading GeoIP databases.")
