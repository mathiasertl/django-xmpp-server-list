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
