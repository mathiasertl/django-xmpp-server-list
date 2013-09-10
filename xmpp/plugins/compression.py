from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import StanzaBase, ElementBase

class CompressionStanza(ElementBase):
    name = 'compression'
    namespace = 'http://jabber.org/features/compress'
    interfaces = set(('required', 'method', ))
    plugin_attrib = name


class feature_compression(BasePlugin):
    """Compression"""

    def plugin_init(self):
        self.description = "Compression"
        self.xmpp.register_feature('compression',
                self._handle_compression,
                restart=False,
                order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, CompressionStanza)

    def _handle_compression(self, features):
        pass
