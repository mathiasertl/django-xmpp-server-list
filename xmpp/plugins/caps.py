from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import ElementBase

class CapsStanza(ElementBase):
    name = 'c'
    namespace = 'http://jabber.org/protocol/caps'
    interfaces = set()
    plugin_attrib = 'caps'


class feature_caps(BasePlugin):
    """Caps"""

    def plugin_init(self):
        self.xmpp.register_feature('c',
                self._handle_caps,
                restart=False,
                order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, CapsStanza)

    def _handle_caps(self, features):
        pass
