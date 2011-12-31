from django.contrib.gis import admin
from models import WorldBorders

admin.site.register(WorldBorders, admin.GeoModelAdmin)