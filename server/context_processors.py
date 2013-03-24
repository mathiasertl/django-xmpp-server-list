from xmpplist.server.util import get_siteinfo

def siteinfo(request):
    protocol, domain = get_siteinfo()
    if request.is_secure():
        protocol = 'https'
    return {
        'domain': domain,
        'protocol': protocol,
        'siteurl': '%s://%s' % (protocol, domain),
    }
