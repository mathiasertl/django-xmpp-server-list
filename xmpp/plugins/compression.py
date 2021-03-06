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
from sleekxmpp.xmlstream import ElementBase
from sleekxmpp.xmlstream import register_stanza_plugin


class CompressionStanza(ElementBase):
    name = 'compression'
    namespace = 'http://jabber.org/features/compress'
    interfaces = set(('required', 'method', ))
    plugin_attrib = name


class feature_compression(BasePlugin):
    """Plugin for Stream Compression (XEP-0138).

    .. seealso:: http://xmpp.org/extensions/xep-0138.html
    """

    def plugin_init(self):
        self.description = 'XEP-0138: Stream Compression'
        self.xmpp.register_feature(
            'compression',
            self._handle_compression,
            restart=False,
            order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, CompressionStanza)

    def _handle_compression(self, features):
        pass
