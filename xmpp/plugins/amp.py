from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import ElementBase

class AmpStanza(ElementBase):
    name = 'amp'
    namespace = 'http://jabber.org/features/iq-amp'
    interfaces = set()
    plugin_attrib = 'iq-amp'


class feature_amp(BasePlugin):
    """Plugin for Advanced Message Processing (XEP-0079).

    .. seealso:: http://www.xmpp.org/extensions/xep-0079.html
    """

    def plugin_init(self):
        self.xmpp.register_feature('amp',
                self._handle_amp,
                restart=False,
                order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, AmpStanza)

    def _handle_amp(self, features):
        pass
