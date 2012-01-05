from django.forms import ModelForm
from django.forms.forms import Form
from django.forms.fields import CharField
from django.forms.widgets import TextInput, DateInput
from django.contrib.gis.admin.widgets import OpenLayersWidget
from django.contrib.gis.geos import Point

from models import Server
import floppyforms

class ServerForm(ModelForm):
    location = CharField(min_length=3, widget=TextInput(attrs={'size': 8, 'class': 'mapwidget'}))
    
    def clean_location(self):
        x, y = self.cleaned_data['location'].split(',')
        return Point(x=float(x), y=float(y))
    
    class Meta:
        model = Server
        fields = (
            'domain', 'website', 'ca', 'ssl_port', 'launched', 'location',
            'contact', 'contact_name', 'contact_type',
        )
        widgets = {
            'ssl_port': TextInput(attrs={'size': 4, 'maxlength': 5}),
            'longitude': TextInput(attrs={'size': 4}),
            'latitude': TextInput(attrs={'size': 4}),
            'domain': TextInput(attrs={'size': 10}),
            'website': TextInput(attrs={'size': 16}),
            'launched': DateInput(attrs={'size': 8, 'class': 'datepicker'}, format='%Y-%m-%d'),
        }
        
#class PointWidget(floppyforms.gis.PointWidget, floppyforms.gis.BaseMetacartaWidget):
#    pass

#class PointWidget(floppyforms.gis.PointWidget, floppyforms.gis.BaseOsmWidget):
#    pass
#    map_srid = 4326
#    map_options = {'projection': 'new OpenLayers.Projection("EPSG:900913")'}
#    mouse_position = False

class PointWidget(floppyforms.gis.PointWidget, floppyforms.gis.BaseGMapWidget):
    pass

class ServerLocationForm(Form):
    osmlocation = floppyforms.gis.PointField(widget=PointWidget)