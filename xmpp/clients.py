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

import logging
import re

from django.conf import settings

from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.basexmpp import BaseXMPP
from sleekxmpp.xmlstream.handler import Callback
from sleekxmpp.xmlstream.matcher import MatchXPath

from xmpp.plugins import amp
from xmpp.plugins import auth
from xmpp.plugins import bind
from xmpp.plugins import caps
from xmpp.plugins import compression
from xmpp.plugins import dialback
from xmpp.plugins import register
from xmpp.plugins import rosterver
from xmpp.plugins import session
from xmpp.plugins import sm

log = logging.getLogger(__name__)


class StreamFeatureClient(BaseXMPP):
    """A client to test c2s stream features.

    :param domain: The domain that this server serves (not the DNS-name
        under which it is available!)
    :param callback: Callback to call with stream features.
    :param cert: Certificate
    """

    def __init__(self, domain, callback, cert, cert_errback, lang='en',
                 ns='jabber:client'):
        super(StreamFeatureClient, self).__init__(domain, default_ns=ns)
        self.use_ipv6 = settings.USE_IP6
        self.auto_reconnect=False
        self.callback = callback
        self.cert_errback = cert_errback
        self.ca_certs = cert

        # copied from ClientXMPP
        self.default_lang = lang
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

        # register known features:
        self.register_plugin('feature_amp', module=amp)
        self.register_plugin('feature_auth', module=auth)
        self.register_plugin('feature_bind', module=bind)
        self.register_plugin('feature_caps', module=caps)
        self.register_plugin('feature_compression', module=compression)
        self.register_plugin('feature_mechanisms')
        self.register_plugin('feature_register', module=register)
        self.register_plugin('feature_session', module=session)
        self.register_plugin('feature_sm', module=sm)
        self.register_plugin('feature_starttls')
        self.register_plugin('feature_rosterver', module=rosterver)
        self.register_plugin('feature_dialback', module=dialback)

        self.register_stanza(StreamFeatures)
        self.register_handler(
            Callback('Stream Features',
                     MatchXPath('{%s}features' % self.stream_ns),
                     self.get_features))

        self.add_event_handler('ssl_invalid_chain', self._cert_errback)
        self.add_event_handler('ssl_invalid_cert', self._cert_errback)

        # do not reparse features:
        self._features = None

    def _cert_errback(self, *args, **kwargs):
        self.disconnect(self.auto_reconnect, send_close=False)
        self.cert_errback(host=self.address[0], port=self.address[1],
                          ssl=self.use_ssl, tls=self.use_tls)

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

    def parse_features(self, features):
        parsed = {}

        found_tags = set([re.match('{.*}(.*)', n.tag).groups(1)[0]
                         for n in features.xml.getchildren()])

        # no XEP, defined here: http://delta.affinix.com/specs/xmppstream.html
        if 'address' in found_tags:
            found_tags.remove('address')

        for name, node in features.get_features().items():
            ns = node.namespace

            if name == 'amp':  # not yet seen in the wild!
                log.error("Untested plugin: %s", node)
                parsed[name] = {}
            elif name == 'bind':  # not yet seen in the wild!
                log.error("Untested plugin: %s", node)
                parsed[name] = {}
            elif name == 'compression':
                methods = [n.text for n
                           in node.findall('{%s}method' % ns)]
                parsed[name] = {'methods': methods, }
            elif name == 'c':  # Entity Capabilities (XEP-0115)
                parsed[name] = {}
            elif name == 'iq-auth':
                parsed['auth'] = {}
            elif name == 'iq-register':
                parsed['register'] = {}
            elif name == 'dialback':
                parsed['dialback'] = {}
            elif name == 'mechanisms':
                mechs = [n.text for n
                         in node.findall('{%s}mechanism' % ns)]
                parsed[name] = {'mechanisms': mechs, }
            elif name == 'session':  # not yet seen in the wild!
                log.error("Untested plugin: %s", node)
                parsed[name] = {}
            elif name == 'sm':  # not yet seen in the wild!
                log.error("Untested plugin: %s", node)
                parsed[name] = {}
            elif name == 'starttls':
                required = node.find('{%s}required' % ns)
                if required is None:
                    parsed[name] = {'required': False, }
                else:
                    parsed[name] = {'required': True, }
            elif name == 'rosterver':  # obsolete, seen on tigase.im
                parsed['ver'] = {}
            else:
                log.warn('Unhandled feature: %s - %s' % (name, node))

        unhandled = found_tags - set(parsed.keys())
        if unhandled:
            log.warn('%s: Unknown stream features: %s',
                     self.boundjid.bare, ', '.join(unhandled))

        # beautify the dict a bit:
        if 'c' in parsed:
            parsed['caps'] = parsed.pop('c')
        if 'ver' in parsed:
            parsed['rosterver'] = parsed.pop('ver')
        if 'mechanisms' in parsed:
            parsed['sasl_auth'] = parsed.pop('mechanisms')

        return parsed

    def get_features(self, features):
        """

        .. NOTE:: A list of features is available `here
            <http://xmpp.org/registrar/stream-features.html>`_
        """
        try:
            if self._features is None:
                self._features = self.parse_features(features)
                self.callback(
                    host=self.address[0], port=self.address[1],
                    features=self._features, ssl=self.use_ssl,
                    tls=self.use_tls)

            # copied from ClientXMPP._handle_stream_features():
            if 'starttls' in features['features']:
                handler, restart = self._stream_feature_handlers['starttls']
                if handler(features) and restart:
                    # Don't continue if the feature requires
                    # restarting the XML stream.
                    return True
            # end copied ClientXMPP._handle_stream_features()

            self.disconnect()
        except Exception as e:
            log.error(e)
            raise
