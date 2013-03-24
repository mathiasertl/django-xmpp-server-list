from urlparse import urlparse

from django.contrib.gis.geos import Point
from django.core import validators
from django.forms import ModelForm
from django.forms.fields import CharField
from django.forms.forms import Form
from django.forms.forms import ValidationError
from django.forms.widgets import DateInput
from django.forms.widgets import TextInput

import floppyforms

from xmpplist.server.models import Server


class ServerForm(ModelForm):
    location = CharField(
        min_length=3, widget=TextInput(
            attrs={'size': 8, 'class': 'mapwidget'}),
        help_text="Where the server is located.")

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

    def clean_location(self):
        try:
            x, y = self.cleaned_data['location'].strip().split(',')
            x = float(x)
            y = float(y)
        except ValueError:
            raise ValidationError(
                "Format for coordinates is 'long,lat', example: 16.37,48.2")

        if x > 180 or x < -180:
            raise ValidationError('Longitude must be between -180 and +180!')
        if y > 90 or y < -90:
            raise ValidationError('Latitude must be between -90 and +90!')
        return Point(x=x, y=y)

    def clean_domain(self):
        domain = self.cleaned_data['domain']
        if not self.verify_domain(domain):
            raise ValidationError(
                'Domain must be a simple domain. Use "%s" instead.'
                % parsed.hostname)
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
            'domain', 'website', 'ca', 'ssl_port', 'launched', 'location',
            'contact_type', 'contact', 'contact_name',
        )
        widgets = {
            'ssl_port': TextInput(attrs={'size': 4, 'maxlength': 5}),
            'longitude': TextInput(attrs={'size': 4}),
            'latitude': TextInput(attrs={'size': 4}),
            'domain': TextInput(attrs={'size': 10}),
            'website': TextInput(attrs={'size': 16}),
            'launched': DateInput(attrs={
                'size': 8, 'class': 'datepicker'}, format='%Y-%m-%d'),
        }


#class PointWidget(floppyforms.gis.PointWidget,
#                  floppyforms.gis.BaseMetacartaWidget):
#    pass

#class PointWidget(floppyforms.gis.PointWidget, floppyforms.gis.BaseOsmWidget):
#    pass
#    map_srid = 4326
#    map_options = {'projection': 'new OpenLayers.Projection("EPSG:900913")'}
#    mouse_position = False


class PointWidget(floppyforms.gis.BaseOsmWidget, floppyforms.gis.PointWidget):
    template_name = 'forms/pointwidget.html'


class ServerLocationForm(Form):
    osmlocation = floppyforms.gis.PointField(widget=PointWidget)
