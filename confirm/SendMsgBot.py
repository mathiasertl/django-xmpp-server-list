# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list)
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# django-xmpp-server-list is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-server-list. If not, see <http://www.gnu.org/licenses/>.

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
    """A basic SleekXMPP bot that will log in, send a message, and then log out."""

    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The message we wish to send, and the JID that will receive it
        self.recipient = recipient
        self.msg = str(message)

        # The session_start event will be triggered when the bot establishes its connection with
        # the server and the XML streams are ready for use. We want to listen for this event so
        # that we we can intialize our roster.
        self.add_event_handler("session_start", self.start)

    def start(self, event):
        """Process the session_start event.

        Typical actions for the session_start event are requesting the roster and broadcasting an
        intial presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.send_message(mto=self.recipient, mbody=self.msg, mtype='chat')

        # Using wait=True ensures that the send queue will be
        # emptied before ending the session.
        self.disconnect(wait=True)
