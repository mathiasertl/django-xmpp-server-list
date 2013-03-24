import hashlib
import logging
import threading
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string

from xmpplist.server.util import get_siteinfo
from xmpplist.server.models import Server
from SendMsgBot import SendMsgBot

CONFIRMATION_TYPE_CHOICES = (
    ('J', 'JID'),
    ('E', 'e-mail'),
)


class ConfirmationKey(models.Model):
    key = models.CharField(max_length=128, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=CONFIRMATION_TYPE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(ConfirmationKey, self).__init__(*args, **kwargs)
        self.key = self.set_random_key()

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
        subject = self.subject % subject_format
        message = render_to_string(self.template, context)

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


class UserConfirmationKey(ConfirmationKey):
    user = models.ForeignKey(User, related_name='confirmations')

    template = 'confirm/user_contact.txt'
    subject = 'Confirm your %(addr_type)s on %(protocol)s://%(domain)s'

    @property
    def recipient(self):
        if self.type == 'E':
            return self.user.email
        elif self.type == 'J':
            return self.user.profile.jid

    def set_random_key(self):
        salt = hashlib.sha1('%s-%s-%s' % (settings.SECRET_KEY, time.time(),
                                             self.type)).hexdigest()
        return hashlib.sha1('%s-%s-%s' % (salt, self.user.username,
                                             self.user.email)).hexdigest()

    @models.permalink
    def get_absolute_url(self):
        return ('confirm_user_contact', (), {'key': self.key})


class UserPasswordResetKey(UserConfirmationKey):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetKey, self).__init__(*args, **kwargs)
        if 'type' not in kwargs:
            if self.user.profile.email_confirmed:
                self.type = 'E'
            else:
                self.type = 'J'

    template = 'confirm/user_password_reset.txt'
    subject = 'Reset your password on %(protocol)s://%(domain)s'

    @models.permalink
    def get_absolute_url(self):
        return ('reset_user_password', (), {'key': self.key})


class ServerConfirmationKey(ConfirmationKey):
    server = models.ForeignKey(Server, related_name='confirmations')

    template = 'confirm/server_contact.txt'
    subject = 'Confirm contact details for %(serverdomain)s on %(protocol)s://%(domain)s'

    def add_context(self):
        return {'serverdomain': self.server.domain}

    @property
    def recipient(self):
        return self.server.contact

    def __init__(self, *args, **kwargs):
        super(ServerConfirmationKey, self).__init__(*args, **kwargs)
        self.type = self.server.contact_type

    def set_random_key(self):
        salt = hashlib.sha1('%s-%s' % (settings.SECRET_KEY,
                                          time.time())).hexdigest()
        return sha_constructor('%s-%s' % (salt,
                                          self.server.domain)).hexdigest()

    @models.permalink
    def get_absolute_url(self):
        return ('confirm_server', (), {'key': self.key})
