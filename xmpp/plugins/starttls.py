from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import StanzaBase, ElementBase

from sleekxmpp.features.feature_starttls.starttls import FeatureSTARTTLS as _orig_plugin
from sleekxmpp.features.feature_starttls.stanza import STARTTLS
from sleekxmpp.features.feature_starttls.stanza import Proceed
from sleekxmpp.features.feature_starttls.stanza import Failure

class MyStanza(STARTTLS):
    def get_required(self):
        return False

class stanza(object):
    STARTTLS = MyStanza
    Proceed = Proceed
    Failure = Failure

class FeatureSTARTTLS(_orig_plugin):
    stanza = stanza
