"""
Code retrieved from
    getting_started/sendlogout.html
from the official SleekXMPP docs
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import sleekxmpp

class SendMsgBot(sleekxmpp.ClientXMPP):
    """
    A basic SleekXMPP bot that will log in, send a message,
    and then log out.
    """

    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The message we wish to send, and the JID that
        # will receive it.
        self.recipient = recipient
        self.msg = str(message)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can intialize
        # our roster.
        self.add_event_handler("session_start", self.start)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an intial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()

        print(self.recipient)
        print(self.msg)
        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')
        print('sent message')

        # Using wait=True ensures that the send queue will be
        # emptied before ending the session.
        self.disconnect(wait=True)