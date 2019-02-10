# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list)
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppllist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.

import textwrap

from django.conf import settings
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

from ..clients import SendMsgBot

DEFAULT_XMPP_BACKEND = getattr(settings, 'DEFAULT_XMPP_BACKEND', 'xmpp.backends.SleekBackend')


class XMPPBackend:
    def send_chat_message(self, to, message):
        raise NotImplementedError('subclasses of XMPPBackend must provide the send_chat_message() method')


class SleekBackend(XMPPBackend):
    def __init__(self, xmpp_credentials='default'):
        self.xmpp_credentials = xmpp_credentials

    def send_chat_message(self, to, message):
        creds = settings.XMPP[self.xmpp_credentials]
        client = SendMsgBot(creds['jid'], creds['password'], to, message)
        if client.connect():
            client.process(wait=True)


class ConsoleBackend(XMPPBackend):
    def send_chat_message(self, to, message):
        print('Sending XMPP message:')
        print('# To: %s' % to)
        print(textwrap.indent(message, '# '))


class DefaultXMPPBackend(LazyObject):
    def _setup(self):
        self._wrapped = get_xmpp_backend()()


def get_xmpp_backend(import_path=None):
    return import_string(import_path or DEFAULT_XMPP_BACKEND)


default_xmpp_backend = DefaultXMPPBackend()
