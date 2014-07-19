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

from __future__ import unicode_literals

from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import ElementBase


class AmpStanza(ElementBase):
    name = 'bind'
    namespace = 'urn:ietf:params:xml:ns:xmpp-bind'
    interfaces = set()
    plugin_attrib = 'bind'


class feature_bind(BasePlugin):
    """Plugin for Resource Binding (RFC 6120: XMPP Core).

    .. seealso:: http://www.ietf.org/rfc/rfc6120.txt
    """

    def plugin_init(self):
        self.description = 'RFC 6120: Stream Feature: Resource Binding'
        self.xmpp.register_feature(
            'bind',
            self._handle_bind,
            restart=False,
            order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, AmpStanza)

    def _handle_bind(self, features):
        pass
