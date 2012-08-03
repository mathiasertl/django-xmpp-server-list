from django.conf import settings
from django.contrib.sites.models import Site

def get_siteinfo():
    site = Site.objects.get_current()

    if settings.USE_HTTPS:
        protocol = 'https'
    else:
        protocol = 'http'

    return protocol, site.domain
