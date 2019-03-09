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

import binascii
import logging
import os
import shutil
import tarfile
import tempfile

import requests

from django.conf import settings

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


def bytes_to_hex(b):
    """Convert a bytes array to hex.

    >>> bytes_to_hex(b'test')
    '74:65:73:74'
    """
    return add_colons(binascii.hexlify(b).upper().decode('utf-8'))


def refresh_geoip_database():
    if not os.path.exists(settings.GEOIP_CONFIG_ROOT):
        os.makedirs(settings.GEOIP_CONFIG_ROOT)

    log.info("Downloading MaxMind GeoIP database...")
    url = 'https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz'

    with requests.get(url, stream=True) as r, tempfile.NamedTemporaryFile() as tmp:
        r.raw.decode_content = True  # decode gzip/deflate compression of response
        shutil.copyfileobj(r.raw, tmp)

        tmp.seek(0)

        with tarfile.open(fileobj=tmp, mode="r:gz") as tar:
            members = [m for m in tar.getmembers() if m.isfile() and os.path.splitext(m.name)[1] == '.mmdb']

            # remove any directory prefix
            for member in members:
                member.name = os.path.basename(member.name)
            log.info('Extracting %s to %s', ', '.join([m.name for m in members]), settings.GEOIP_CONFIG_ROOT)

            tar.extractall(settings.GEOIP_CONFIG_ROOT, members)
