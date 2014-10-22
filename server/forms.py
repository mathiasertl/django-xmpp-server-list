# -*- coding: utf-8 -*-
#
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

from urlparse import urlparse

from django.core import validators
from django.forms import ModelForm
from django.forms.forms import ValidationError
from django.forms.widgets import DateInput
from django.forms.widgets import Select
from django.forms.widgets import TextInput

from server.models import Server


class ServerForm(ModelForm):
    def verify_domain(self, value):
        """
        verify a domain (we need this in multiple places)
        """
        parsed = urlparse('//%s' % value)

        if parsed.scheme or parsed.path or parsed.params or parsed.query or \
                parsed.fragment or parsed.username or parsed.password or \
                parsed.port:
            return False
        return True

    def contact_changed(self):
        changed = self.changed_data
        if 'contact' in changed or 'contact_type' in changed:
            return True
        return False

    def clean_ssl_port(self):
        ssl_port = self.cleaned_data['ssl_port']
        if ssl_port > 65535:
            raise ValidationError("Maximum port number is 65545.")
        return ssl_port

    def clean_domain(self):
        try:
            domain = self.cleaned_data['domain']

            if not self.verify_domain(domain):
                raise ValidationError(
                    'Domain must be a simple domain, i.e. "example.com"')
        except:
            raise ValidationError("Could not parse domain.")
        return domain

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        if not contact:
            return contact

        typ = self.cleaned_data['contact_type']

        if typ == 'E':  # email
            validators.validate_email(contact)
        elif typ in ['M', 'J']:  # MUC or JID
            if typ == 'M':
                typname = 'MUC'
            else:
                typname = 'JID'

            if '@' not in contact or contact.count('@') > 1:
                raise ValidationError('Please enter a valid %s.' % typname)

            user, domain = contact.split('@')
            if not self.verify_domain(domain):
                raise ValidationError('Please enter a valid %s.' % typname)

        elif typ == 'W':  # website
            parsed = urlparse(contact)
            if not (parsed.scheme and parsed.netloc):
                raise ValidationError('Please enter a valid URL.')
        else:
            raise ValidationError('no more cheese exception.')

        return contact

    def save(self, commit=True):
        server = super(ServerForm, self).save(commit=False)
        if self.contact_changed():
            server.contact_verified = False
        if commit:
            server.save()

        return server

    class Meta:
        model = Server
        fields = (
            'domain', 'website', 'launched', 'contact_type', 'contact', 'contact_name',
        )
        widgets = {
            'contact_type': Select(attrs={'class': 'contact_type', }),
            'longitude': TextInput(attrs={'size': 4}),
            'latitude': TextInput(attrs={'size': 4}),
            'domain': TextInput(attrs={'size': 10}),
            'website': TextInput(attrs={'size': 16}),
            'launched': DateInput(attrs={
                'size': 8, 'class': 'datepicker'}, format='%Y-%m-%d'),
        }
