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


class RegisterStanza(ElementBase):
    name = 'register'
    namespace = 'http://jabber.org/features/iq-register'
    interfaces = set()
    plugin_attrib = 'iq-register'


class feature_register(BasePlugin):
    """Plugin for In-Band Registration (XEP-0077).

    .. seealso:: http://www.xmpp.org/extensions/xep-0077.html
    """

    def plugin_init(self):
        self.description = 'XEP-0077: In-Band Registration'
        self.xmpp.register_feature(
            'register',
            self._handle_register,
            restart=False,
            order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, RegisterStanza)

    def _handle_register(self, features):
        pass
