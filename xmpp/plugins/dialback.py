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

from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import ElementBase


class DialbackStanza(ElementBase):
    name = 'dialback'
    namespace = 'urn:xmpp:features:dialback'
    interfaces = set()
    plugin_attrib = 'dialback'


class feature_dialback(BasePlugin):
    """Plugin for Server Dialback (XEP-0220).

    .. seealso:: http://www.xmpp.org/extensions/xep-0077.html
    """

    def plugin_init(self):
        self.description = 'XEP-0220: Server Dialback'
        self.xmpp.register_feature(
            'dialback',
            self._handle_dialback,
            restart=False,
            order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, DialbackStanza)

    def _handle_dialback(self, features):
        pass
