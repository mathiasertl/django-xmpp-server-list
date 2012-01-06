import json

from django.core import serializers
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from xmpplist.server.models import Server
from xmpplist.world.models import WorldBorders

def index(request):
    # initial query-set:
    servers = Server.objects.filter(
        verified=True, moderated=True, user__profile__email_confirmed=True)
    
    # filter by required features:
    if 'features' in request.GET:
        features = request.GET['features'].split(',')
        if 'plain' in features:
            servers = servers.filter(features__has_plain=True)
        if 'ssl' in features:
            servers = servers.filter(features__has_ssl=True)
        if 'tls' in features:
            servers = servers.filter(features__has_tls=True)
        if 'ipv6' in features:
            servers = servers.filter(features__has_ipv6=True)
    
    # filter by country
    if 'country' in request.GET:
        country = WorldBorders.objects.get(iso2__iexact=request.GET['country'])
        servers = servers.filter(location__within=country.geom)
    
    fields = ['domain']
    if 'fields' in request.GET:
        custom_fields = request.GET['fields'].split(',')
        valid_fields = ['launched', 'location', 'website', 'ca', 'software',
                        'software_version', 'contact']
        if set(custom_fields) - set(valid_fields):
            return HttpResponseForbidden("tried to retrieve forbidden fields.")
            
        if 'ca' in custom_fields:
            custom_fields.remove('ca')
            custom_fields.append('ca__name')
        if 'software' in custom_fields:
            custom_fields.remove('software')
            custom_fields.append('software__name')
        if 'contact' in custom_fields:
            custom_fields.remove('contact')
            custom_fields += ['contact', 'contact_type']
            
        fields += custom_fields
    
    if len(fields) == 1:
        values = list(servers.values_list(*fields, flat=True))
    else:
        tmp_values = list(servers.values(*fields))
        values = {}
        for value in tmp_values:
            domain = value.pop('domain')
            
            if 'ca__name' in value:
                ca = value.pop('ca__name')
                value['ca'] = ca
            if 'software__name' in value:
                software = value.pop('software__name')
                value['software'] = software
            if 'contact' in value:
                contact = value.pop('contact')
                contact_type = value.pop('contact_type')
                value['contact'] = (contact, contact_type)
            if 'location' in value:
                location = value.pop('location')
                value['location'] = '%s,%s' % (location.x, location.y)
            if 'launched' in value:
                launched = value.pop('launched')
                value['launched'] = launched.strftime('%Y-%m-%d')
                
            values[domain] = value
    
    return HttpResponse(json.dumps(values))
    
def help(request):
    return render(request, 'api/help.html')