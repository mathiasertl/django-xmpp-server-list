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

from __future__ import unicode_literals


class CONTACT_TYPES(object):
    MUC = 'M'
    JID = 'J'
    EMAIL = 'E'
    WEBSITE = 'W'


CONTACT_TYPE_CHOICES = (
    (CONTACT_TYPES.MUC, 'MUC'),
    (CONTACT_TYPES.JID, 'JID'),
    (CONTACT_TYPES.EMAIL, 'e-mail'),
    (CONTACT_TYPES.WEBSITE, 'website'),
)
C2S_STREAM_FEATURES = {
    'auth',
    'caps',
    'compression',
    'register',
    'rosterver',
    'sasl_auth',
    'starttls',
}
S2S_STREAM_FEATURES = {
    'caps',
    'dialback',
    'starttls',
}
