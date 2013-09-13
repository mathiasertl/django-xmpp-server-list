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
        self.xmpp.register_feature('bind',
                self._handle_bind,
                restart=False,
                order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, AmpStanza)

    def _handle_bind(self, features):
        pass
