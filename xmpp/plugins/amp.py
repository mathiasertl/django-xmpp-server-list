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


class AmpStanza(ElementBase):
    name = 'amp'
    namespace = 'http://jabber.org/features/amp'
    interfaces = set()
    plugin_attrib = 'amp'


class feature_amp(BasePlugin):
    """Plugin for Advanced Message Processing (XEP-0079).

    .. seealso:: http://www.xmpp.org/extensions/xep-0079.html
    """

    def plugin_init(self):
        self.description = 'XEP-0079: Advanced Message Processing'
        self.xmpp.register_feature(
            'amp',
            self._handle_amp,
            restart=False,
            order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, AmpStanza)

    def _handle_amp(self, features):
        pass
