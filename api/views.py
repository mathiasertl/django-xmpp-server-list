import json

from django.http import HttpResponse
from django.core import serializers

from xmpplist.server.models import Server
from xmpplist.world.models import WorldBorders

def index(request):
    # initial query-set:
    servers = Server.objects.filter(
        verified=True, moderated=True, user__profile__email_confirmed=True)
    
    # filter by required features:
    if 'require' in request.GET:
        features = request.GET['require'].split(',')
        if 'plain' in features:
            servers = servers.filter(support_plain=True)
        if 'ssl' in features:
            servers = servers.filter(support_ssl=True)
        if 'tls' in features:
            servers = servers.filter(support_tls=True)
        if 'ipv6' in features:
            servers = servers.filter(features__ipv6=True)
    
    # filter by country
    if 'country' in request.GET:
        country = WorldBorders.objects.get(iso2=request.GET['country'])
        servers = servers.filter(location__within=country.geom)
    
    fields = ['domain']
    if 'fields' in request.GET:
        custom_fields = set(request.GET['fields'].split())
        valid_fields = set(['launched', 'location', 'website', 'ca', 'software',
                            'software_version', 'contact'])
        if custom_fields - valid_fields:
            return HttpResponseForbidden("tried to retrieve forbidden fields.")
            
        if 'ca' in custom_fields:
            custom_fields.pop('ca')
            custom_fields.append('ca__name')
        if 'software' in custom_fields:
            custom_fields.pop('software')
            custom_fields.append('software__name')
        if 'contact' in custom_fields:
            custom_fields.pop('contact')
            custom_fields += ['contact', 'contact_type']
            
        fields += custom_fields
    
    if len(fields) == 1:
        values = list(servers.values_list(*fields, flat=True))
    else:
        values = list(servers.values(*fields))
    
    return HttpResponse(json.dumps(values))