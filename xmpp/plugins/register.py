from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import StanzaBase, ElementBase

class RegisterStanza(ElementBase):
    name = 'register'
    namespace = 'http://jabber.org/features/iq-register'
    interfaces = set()
    plugin_attrib = name


class feature_register(BasePlugin):
    """Register"""

    def plugin_init(self):
        self.xmpp.register_feature('register',
                self._handle_register,
                restart=False,
                order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, RegisterStanza)

    def _handle_register(self, features):
        pass
