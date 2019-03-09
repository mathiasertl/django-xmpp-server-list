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

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse

from server.models import Server
from xmpp.backends import default_xmpp_backend

from .querysets import ConfirmationKeyQuerySet
from .querysets import ServerConfirmationKeyQuerySet


class ConfirmationKey(models.Model):
    TYPE_JID = 'J'
    TYPE_EMAIL = 'E'
    TYPE_CHOICES = (
        (TYPE_JID, 'JID'),
        (TYPE_EMAIL, 'e-mail'),
    )

    key = models.CharField(max_length=128, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    objects = ConfirmationKeyQuerySet.as_manager()

    def __init__(self, *args, **kwargs):
        super(ConfirmationKey, self).__init__(*args, **kwargs)

    def send_mail(self, to, subject, message):
        frm = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, frm, [to], fail_silently=True)

    def send_jid(self, to, message):
        default_xmpp_backend.send_chat_message(to, message)

    def send(self, protocol, domain):
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
            self.send_jid(self.recipient, message)
        else:
            raise RuntimeError("Confirmation messages can only be sent to JIDs or email addresses")

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
    subject = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='confirmations')

    message_template = 'confirm/user_contact.txt'
    message_subject = 'Confirm your %(addr_type)s on %(protocol)s://%(domain)s'

    def confirm(self):
        if self.type == 'E':
            self.subject.email_confirmed = True
        elif self.type == 'J':
            self.subject.jid_confirmed = True
        self.subject.save()

    def get_absolute_url(self):
        return reverse('confirm:user_contact', kwargs={'key': self.key})


class ServerConfirmationKey(ConfirmationKey):
    subject = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='confirmations')
    objects = ServerConfirmationKeyQuerySet.as_manager()

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
        if self.id:
            self.type = self.subject.contact_type

    def confirm(self):
        self.subject.contact_verified = True
        self.subject.save()

    def __str__(self):
        return self.subject.domain

    @property
    def user(self):
        return self.subject.user

    def get_absolute_url(self):
        return reverse('confirm:server', kwargs={'key': self.key})
