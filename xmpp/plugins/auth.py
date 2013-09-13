from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import ElementBase

class AuthStanza(ElementBase):
    name = 'auth'
    namespace = 'http://jabber.org/features/iq-auth'
    interfaces = set()
    plugin_attrib = 'iq-auth'


class feature_auth(BasePlugin):
    """auth (XEP-0078)"""

    def plugin_init(self):
        self.xmpp.register_feature('auth',
                self._handle_auth,
                restart=False,
                order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, AuthStanza)

    def _handle_auth(self, features):
        pass
