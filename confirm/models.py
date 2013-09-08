# -*- coding: utf-8 -*-
#
# This file is part of xmpplist (https://list.jabber.at).
#
# xmpplist is free software: you can redistribute it and/or modify
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
# along with xmpplist.  If not, see <http://www.gnu.org/licenses/>.

import logging
import threading

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string

from xmpplist.server.util import get_siteinfo
from xmpplist.server.models import Server
from SendMsgBot import SendMsgBot

from managers import ConfirmationKeyManager
from managers import ServerConfirmationKeyManager

CONFIRMATION_TYPE_CHOICES = (
    ('J', 'JID'),
    ('E', 'e-mail'),
)


class ConfirmationKey(models.Model):
    key = models.CharField(max_length=128, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=CONFIRMATION_TYPE_CHOICES)

    objects = ConfirmationKeyManager()

    def __init__(self, *args, **kwargs):
        super(ConfirmationKey, self).__init__(*args, **kwargs)

    def send_mail(self, to, subject, message):
        frm = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, frm, [to], fail_silently=True)

    def send_jid(self, to, subject, message):
        creds = settings.XMPP['default']
        logging.basicConfig()

        def send_msg(frm, pwd, to, msg):
            xmpp = SendMsgBot(frm, pwd, to, msg)
            if xmpp.connect():
                xmpp.process(wait=True)

        targs = (creds['jid'], creds['password'], to, message, )
        t = threading.Thread(target=send_msg, args=targs)
        t.daemon = True
        t.start()

    def send(self):
        # build context
        protocol, domain = get_siteinfo()
        context = {'domain': domain, 'key': self, 'protocol': protocol}
        subject_format = {
            'addr_type': self.address_type,
            'domain': domain,
            'protocol': protocol,
        }
        context.update(self.add_context())
        subject_format.update(self.add_context())

        # build subject and message-text
        subject = self.message_subject % subject_format
        message = render_to_string(self.message_template, context)

        # send message
        if self.type == 'E':
            self.send_mail(self.recipient, subject, message)
        elif self.type == 'J':
            self.send_jid(self.recipient, subject, message)
        else:
            raise RuntimeError("Confirmation messages can only be sent to JIDs"
                               "or email addresses")

    def add_context(self):
        return {}

    @property
    def address_type(self):
        if self.type == 'E':
            return 'email address'
        elif self.type == 'J':
            return 'JID'
        else:
            return 'UNKNOWN'

    class Meta:
        abstract = True


class UserConfirmationMixin(object):
    @property
    def user(self):
        return self.subject

    @property
    def recipient(self):
        if self.type == 'E':
            return self.subject.email
        elif self.type == 'J':
            return self.subject.jid


class UserConfirmationKey(ConfirmationKey, UserConfirmationMixin):
    subject = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='confirmations')

    message_template = 'confirm/user_contact.txt'
    message_subject = 'Confirm your %(addr_type)s on %(protocol)s://%(domain)s'

    def confirm(self):
        if self.type == 'E':
            self.subject.email_confirmed = True
        elif self.type == 'J':
            self.subject.jid_confirmed = True
        self.subject.save()

    @models.permalink
    def get_absolute_url(self):
        return ('confirm_user_contact', (), {'key': self.key})


class UserPasswordResetKey(ConfirmationKey, UserConfirmationMixin):
    subject = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='password_resets')

    message_template = 'confirm/user_password_reset.txt'
    message_subject = 'Reset your password on %(protocol)s://%(domain)s'

    def __init__(self, *args, **kwargs):
        super(UserPasswordResetKey, self).__init__(*args, **kwargs)
        if 'type' not in kwargs:
            if self.subject.email_confirmed:
                self.type = 'E'
            else:
                self.type = 'J'

    def confirm(self):
        pass

    @models.permalink
    def get_absolute_url(self):
        return ('reset_user_password', (), {'key': self.key})


class ServerConfirmationKey(ConfirmationKey):
    subject = models.ForeignKey(Server, related_name='confirmations')
    objects = ServerConfirmationKeyManager()

    message_template = 'confirm/server_contact.txt'
    message_subject = 'Confirm contact details for %(serverdomain)s on '
    '%(protocol)s://%(domain)s'

    def add_context(self):
        return {'serverdomain': self.subject.domain}

    @property
    def recipient(self):
        return self.subject.contact

    def __init__(self, *args, **kwargs):
        super(ServerConfirmationKey, self).__init__(*args, **kwargs)
        self.type = self.subject.contact_type

    def confirm(self):
        self.subject.contact_verified = True
        self.subject.save()

    @property
    def user(self):
        return self.subject.user

    @models.permalink
    def get_absolute_url(self):
        return ('confirm_server', (), {'key': self.key})
