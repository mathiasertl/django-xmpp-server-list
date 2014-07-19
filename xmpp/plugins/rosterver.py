# -*- coding: utf-8 -*-
#
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

from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import ElementBase


class RosterVerStanza(ElementBase):
    name = 'ver'
    namespace = 'urn:xmpp:features:rosterver'
    interfaces = set()
    plugin_attrib = 'ver'


class feature_rosterver(BasePlugin):
    """Plugin for Roster Versioning (XEP-0237).

    .. seealso:: http://www.xmpp.org/extensions/xep-0237.html
    """

    def plugin_init(self):
        self.description = 'XEP-0237: Roster Versioning (obsolete)'
        self.xmpp.register_feature(
            'ver',
            self._handle_rosterver,
            restart=False,
            order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, RosterVerStanza)

    def _handle_rosterver(self, features):
        pass
