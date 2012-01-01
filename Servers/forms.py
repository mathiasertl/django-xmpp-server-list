from django.forms import ModelForm
from django.forms.widgets import TextInput, DateInput

from models import Server

class ServerForm(ModelForm):
    class Meta:
        model = Server
        fields = (
            'domain', 'website', 'ca_authority', 'launched', 'longitude', 'latitude', 'ssl_port',
            'contact', 'contact_name', 'contact_type'
        )
        widgets = {
            'ssl_port': TextInput(attrs={'size': 4, 'maxlength': 5}),
            'longitude': TextInput(attrs={'size': 4}),
            'latitude': TextInput(attrs={'size': 4}),
            'domain': TextInput(attrs={'size': 10}),
            'website': TextInput(attrs={'size': 16}),
            'launched': DateInput(attrs={'size': 10}),
        }