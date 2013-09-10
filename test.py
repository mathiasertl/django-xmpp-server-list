import logging

from xmpp.clients import ClientFeatures

logging.basicConfig(level=logging.WARN,
                    format='%(levelname)-8s %(message)s')

xmpp = ClientFeatures('jabber.ccc.de')
xmpp.connect(host='jabber.ccc.de', port=5222)
xmpp.process()
print(xmpp.features)
