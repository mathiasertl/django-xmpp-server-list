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

from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.basexmpp import BaseXMPP
from sleekxmpp.xmlstream.handler import Callback
from sleekxmpp.xmlstream.matcher import MatchXPath

from xmpp.plugins import caps
from xmpp.plugins import compression
from xmpp.plugins import register
from xmpp.plugins import starttls


class ClientFeatures(BaseXMPP):
    def __init__(self, jid):
        super(ClientFeatures, self).__init__(jid, 'jabber:client')

        self.stream_header = "<stream:stream to='%s' %s %s %s %s>" % (
                self.boundjid.host,
                "xmlns:stream='%s'" % self.stream_ns,
                "xmlns='%s'" % self.default_ns,
                "xml:lang='%s'" % self.default_lang,
                "version='1.0'")
        self.stream_footer = "</stream:stream>"
        self.features = set()
        self._stream_feature_handlers = {}
        self._stream_feature_order = []

        # try to register features
        self.register_plugin('feature_mechanisms')
        self.register_plugin('feature_starttls', module=starttls)
        self.register_plugin('feature_compression', module=compression)
        self.register_plugin('feature_caps', module=caps)
        self.register_plugin('feature_register', module=register)

        self.register_stanza(StreamFeatures)
        self.register_handler(
            Callback('Stream Features',
                      MatchXPath('{%s}features' % self.stream_ns),
                      self.get_features))

    def register_feature(self, name, handler,  restart=False, order=5000):
        """Register a stream feature handler.

        :param name: The name of the stream feature.
        :param handler: The function to execute if the feature is received.
        :param restart: Indicates if feature processing should halt with
                        this feature. Defaults to ``False``.
        :param order: The relative ordering in which the feature should
                      be negotiated. Lower values will be attempted
                      earlier when available.
        """
        self._stream_feature_handlers[name] = (handler, restart)
        self._stream_feature_order.append((order, name))
        self._stream_feature_order.sort()

    def get_features(self, features):
        print(features)
        for name, feature in features.get_features().items():
            print('feature: %s (%s)' % (name, feature['required']))
        self.disconnect()
