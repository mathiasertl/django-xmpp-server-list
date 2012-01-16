import ssl, socket, logging
from xml.etree import ElementTree

import dns.resolver

#from django.db import models
from django.contrib.gis.db import models
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

from xmpplist.world.models import WorldBorders

logger = logging.getLogger('xmpplist.server')

def get_addr_str(af, args, hostname):
    if af == socket.AF_INET:
        return '%s:%s (%s)' % (args[0], args[1], hostname)
    elif af == socket.AF_INET6:
        return '[%s]:%s (%s)' % (args[0], args[1], hostname)

def get_hosts(host, port, ipv4=True, ipv6=True):
    hosts = []
    if not settings.CHECK_IPV6:
        ipv6 = False
    
    try:
        if ipv4:
            hosts += socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if ipv6:
            hosts += socket.getaddrinfo(host, port, socket.AF_INET6, socket.SOCK_STREAM)
            
        return hosts
    except Exception as e:
        return []
        
def get_stream_features(sock, server, certificate, xmlns='jabber:client'):
    """
    <stream:stream xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' id='00a5101e-4e49-43b8-8449-670a862d33f7' from='gajim.org' version='1.0' xml:lang='en'>
        <stream:features>
            <mechanisms xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>
                <mechanism>SCRAM-SHA-1</mechanism>
                <mechanism>DIGEST-MD5</mechanism>
            </mechanisms>
            <starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>
        </stream:features>
    """
    features = set()
    
    try:
        msg = """<stream:stream xmlns='%s'
            xmlns:stream='http://etherx.jabber.org/streams'
            to='%s' version='1.0'>""" %(xmlns, server)
        sock.send( msg.encode( 'ascii' ) )
        resp = sock.recv(4096).decode( 'utf-8' )
        if not resp: # happens at sternenschweif.de
            raise RuntimeError('no answer received!')
            
        while not resp.endswith( '</stream:features>' ):
            resp += sock.recv(4096).decode( 'utf-8' )
        
        #elem = ElementTree.parse(resp)
        elem = ElementTree.fromstring(resp + '</stream:stream>')
        elem = elem.find('{http://etherx.jabber.org/streams}features')
        
        starttls = elem.find('{urn:ietf:params:xml:ns:xmpp-tls}starttls')
        if starttls is not None:
            features.add('starttls')
        if starttls is None or starttls.find('{urn:ietf:params:xml:ns:xmpp-tls}required') is None:
            features.add('plain')
        if elem.find('{http://jabber.org/features/iq-register}register') is not None:
            features.add('register')
            
        if 'starttls' in features:
            sock.send( '''<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>'''.encode( 'ascii' ) )
            resp += sock.recv(4096).decode('utf-8')
            try:
                if certificate:
                    kwargs = {'cert_reqs': ssl.CERT_REQUIRED, 'ca_certs': certificate}
                else:
                    kwargs = {'cert_reqs': ssl.CERT_NONE}
                ssl_sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1, **kwargs)
                ssl_sock.close()
            except ssl.SSLError as e:
                logger.error(e)
            
        # close stream again:
        sock.send('</stream:stream>'.encode('ascii'))
        sock.recv(4096)
    except Exception as e:
        logger.error('Exception while getting stream features: %s' % e)
        
    return features

def check_hostname(hostname, port, ipv4=True, ipv6=True,
                   domain='', cert='', xmlns='jabber:client'):
    """
    Returns True if all addresses for the given host are reachable on the given port.
    
    :param hostname: A hostname specified by an SRV record.
    :param     port: A port specified by an SRV record.
    :param     ipv4: If False, IPv4 addresses are not checked.
    :param     ipv6: If False, IPv6 addresses are not checked.
    :param   domain: If given, XML stream features will be checked.
    :param    xmlns: The XML stream namespace used if XML stream features are checked
    """
    logger.debug('Verify connectivity for %s %s (IPv4: %s, IPv6: %s)', hostname, port, ipv4, ipv6)
    features = set()
    hosts = get_hosts(hostname, port, ipv4, ipv6)
    if not hosts:
        logger.error('%s: No hosts returned (IPv4: %s, IPv6: %s)' % (hostname, ipv4, ipv6))
        return False, features
    first_iter = True

    for af, socktype, proto, canonname, connect_args in hosts:
        if af == socket.AF_INET:
            addr_str = '%s:%s (%s)' % (connect_args[0], connect_args[1], hostname)
        elif af == socket.AF_INET6:
            addr_str = '[%s]:%s (%s)' % (connect_args[0], connect_args[1], hostname)
        
        try:
            s = socket.socket(af, socktype, proto)
            s.settimeout(1.0)
            s.connect(connect_args)
            
            if domain:
                if first_iter:
                    features = get_stream_features(s, domain, cert, xmlns)
                    first_iter = False
                else:
                    features &= get_stream_features(s, domain, cert, xmlns)
                    
            s.close()
        except socket.error as e:
            logger.error('%s: %s' % (addr_str, e))
            return False, features
        except:
            logger.error('Failed to connect to %s' % addr_str)
            return False, features
        
    return True, features

def check_hostname_ssl(hostname, port, cert, ipv4=True, ipv6=True):
    """
    Returns True if all addresses the given hostname resolves to are reachable on the given
    port and if SSL negotiation with the given certificate succeeds.
    
    :param hostname: A hostname.
    :param port: A port.
    :param ipv4: If False, IPv4 addresses are not checked.
    :param ipv6: If False, IPv6 addresses are not checked.
    """
    logger.debug('Verify SSL connectivity for %s %s (IPv4: %s, IPv6: %s)', hostname, port, ipv4, ipv6)
    hosts = get_hosts(hostname, int(port), ipv4, ipv6)
    if not hosts:
        logger.error('%s (SSL): No hosts returned (IPv4: %s, IPv6: %s)' % (hostname, ipv4, ipv6))
        return False
    
    for af, socktype, proto, canonname, connect_args in hosts:
        if af == socket.AF_INET:
            addr_str = '%s:%s (%s)' % (connect_args[0], connect_args[1], hostname)
        elif af == socket.AF_INET6:
            addr_str = '[%s]:%s (%s)' % (connect_args[0], connect_args[1], hostname)
            
        try:
            s = socket.socket(af, socktype, proto)
            s.settimeout(1.0)
            s.connect(connect_args)
            if cert:
                kwargs = {'cert_reqs': ssl.CERT_REQUIRED, 'ca_certs': cert}
            else:
                kwargs = {'cert_reqs': ssl.CERT_NONE}
            ssl_sock = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1, **kwargs)
            ssl_sock.close()
            s.close()
        except socket.error as e:
            logger.error('%s: %s' % (addr_str, e))
            return False
        except Exception as e:
            logger.error('Failed to connect to %s' % addr_str)
            return False
    
    return True

class CertificateAuthority(models.Model):
    name = models.CharField(max_length=30, unique=True)
    website = models.URLField(unique=True)
    certificate = models.FilePathField(path=settings.CERTIFICATES_PATH, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
class ServerSoftware(models.Model):
    name = models.CharField(max_length=16)
    website = models.URLField()
    newest_version = models.CharField(max_length=8)
    
    def __unicode__(self):
        return self.name

class ServerReport(models.Model):
    """
    Server problem report. If a field is true, it means that the given problem exists.
    """
    created = models.DateField(auto_now_add=True)
    
    srv_client = models.BooleanField(default=True)
    srv_server = models.BooleanField(default=True)
    
    client_online = models.BooleanField(default=True)
    server_online = models.BooleanField(default=True)
    
    ssl_cert = models.BooleanField(default=True)
    tls_cert = models.BooleanField(default=True)
    
    def srv_lookup(self, service, proto='tcp'):
        """
        Function for doing SRV-lookups. Returns a list of host/port tuples for
        the given srv-record.
        """
        record = '_%s._%s.%s' % (service, proto, self.server.domain)
        try:
            resolver = dns.resolver.Resolver()
            resolver.lifetime = 3.0
            answers = resolver.query(record, 'SRV')
        except:
            return []
        hosts = []
        for answer in answers:
            hosts.append((answer.target.to_text(True), answer.port, answer.priority))
        return sorted(hosts, key=lambda host: host[2])

    def verify_srv_client(self):
        """
        Verify xmpp-client SRV records.
        
        This test succeeds if the 'xmpp-client' SRV record has one or more entries.
        """
        hosts = self.srv_lookup('xmpp-client')
        if hosts:
            self.srv_client = True
        else:
            self.srv_client = False
        
        return hosts
            
    def verify_srv_server(self):
        """
        Verify xmpp-server SRV records.
        
        This test succeeds if the 'xmpp-server' SRV record has one or more entries.
        """
        hosts = self.srv_lookup('xmpp-server')
        if hosts:
            self.srv_server = True
        else:
            self.srv_server = False
            
        return hosts
            
    def verify_client_online(self, records, ipv4=True, ipv6=True):
        """
        Verify that at least one of the hosts referred to by the xmpp-client SRV records is
        currently online.
        """
        hostnames_online = []
        features = set()
        if not self.srv_client:
            return hostnames_online, features
        
        first_iter = True
        
        for hostname, port, priority in records:
            domain = self.server.domain
            cert = self.server.ca.certificate
            online, myfeatures = check_hostname(
                hostname, port, ipv4=ipv4, ipv6=ipv6, domain=domain, cert=cert
            )
            if online:
                hostnames_online.append((hostname, port, priority))
                if first_iter:
                    features = myfeatures
                    first_iter = False
                else:
                    features &= myfeatures
                
        if 'starttls' in features:
            self.tls_cert = True
        else:
            self.tls_cert = False
            
        if hostnames_online:
            self.client_online = True
        else:
            self.client_online = False
        
        return hostnames_online, features
            
    def verify_server_online(self, hosts, ipv4=True, ipv6=True):
        """
        Verify that at least one of the hosts referred to by the xmpp-server SRV records is
        currently online.
        """
        if not self.srv_server:
            return []
        
        hosts_online = []
        for host in hosts:
            online, features = check_hostname(host[0], host[1], ipv4, ipv6)
            if online:
                hosts_online.append(host)
                
        if hosts_online:
            self.server_online = True
        else:
            self.server_online = False
        return hosts_online
            
    def verify_ssl(self, hosts, ca, ssl_port, ipv4=True, ipv6=True):
        """
        Verify SSL connectivity.
        
        This test succeeds if all IP addresses that 'host' resolves to are reachable on the given
        port and SSL negotiation succeeds with the given certificate.
        """
        self.ssl_cert = True
        for host, port, priority in hosts:
            if not check_hostname_ssl(host, ssl_port, ca.certificate, ipv4, ipv6):
                self.ssl_cert = False
                logger.error('%s: SSL-connectivity failed on %s %s', self.server.domain, host, ssl_port)
                return
            
    def verify_tls(self, client_hosts):
        if not srv_client:
            return
        
        for host in hosts:
            pass
    
    def is_ok(self):
        return self.srv_client and self.srv_server and self.client_online and self.server_online \
            and self.ssl_cert and self.tls_cert
    
    def has_problems(self):
        return not self.is_ok()
    
    def __unicode__(self):
        try:
            domain = self.server.domain
        except:
            domain = 'INVALID SERVER!'
            
        condition = 'ok'
        if self.has_problems():
            condition = 'has problems'
        return 'Report on %s: %s' % (domain, condition)

class Features(models.Model):
    # connection-related:
    has_plain = models.BooleanField(default=False)
    has_ssl = models.BooleanField(default=False)
    has_tls = models.BooleanField(default=False)
    has_ipv6 = models.BooleanField(default=False)
    has_ibr = models.BooleanField(default=False)
    
    # features:
    has_muc = models.BooleanField(default=False)
    has_irc = models.BooleanField(default=False)
    has_vcard = models.BooleanField(default=False)
    has_pep = models.BooleanField(default=False)
    has_proxy = models.BooleanField(default=False)
    has_webpresence = models.BooleanField(default=False)
    
    def __unicode__(self):
        try:
            domain = self.server.domain
        except:
            domain = 'INVALID SERVER!'
            
        return 'Features for %s' % (domain)
    
    def check_ipv6(self, servers):
        """
        Check for correct IPv6 DNS entries.
        
        This test succeeds if all servers returned by the xmpp-client lookup have a AAAA record.
        """
        if not self.server.report.srv_client:
            return
        
        self.has_ipv6 = True
        for hostname, port, priority in servers:
            try:
                if not get_hosts(hostname, port, False, True):
                    self.has_ipv6 = False
                    break
            except:
                self.has_ipv6 = False
                break

from django.contrib.gis.geos import Point

class Server(models.Model):
    class Meta:
        permissions = (
            ('moderate', 'can moderate servers'),
        )
        
    # basic information:
    user = models.ForeignKey(User, related_name='servers')
    added = models.DateField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    launched = models.DateField(help_text="When the server was launched.")
    location = models.PointField(default=Point(0,0), help_text="Where the server is located.")
    
    # information about the service:
    domain = models.CharField(unique=True, max_length=30,
        help_text="The primary domain of your server.")
    website = models.URLField(blank=True,
        help_text="A homepage where one can find information on your server. If left empty, "
            "the default is http://<domain>.")
    ca = models.ForeignKey(CertificateAuthority, related_name='servers', verbose_name='CA',
        help_text="The Certificate Authority of the certificate used in SSL/TLS connections.")
    ssl_port = models.PositiveIntegerField(default=5223, blank=True, null=True,
        verbose_name='SSL port',
        help_text="The Port where your server allows SSL connections. Leave empty if your server "
            "does not allow SSL connections.")
    
    # verification
    verified = models.NullBooleanField(default=None)
    report = models.OneToOneField(ServerReport, related_name='server')
    
    # moderation:
    moderated = models.NullBooleanField(default=None)
    features = models.OneToOneField(Features, related_name='server')
    
    # queried information
    software = models.ForeignKey(ServerSoftware, related_name='servers', null=True, blank=True)
    software_version = models.CharField(max_length=16, blank=True)
    
    objects = models.GeoManager()
    
    # contact information
    CONTACT_TYPE_CHOICES=(
        ('M', 'MUC'),
        ('J', 'JID'),
        ('E', 'e-mail'),
        ('W', 'website'),
    )
    contact = models.CharField(max_length=30,
        help_text="The address where the server-admins can be reached.")
    contact_type = models.CharField(max_length=1, choices=CONTACT_TYPE_CHOICES, default='J',
        help_text="What type your contact details are. This setting will affect how the contact "
            "details are rendered on the front page. If you choose a JID or an e-mail address, you "
            "will receive an automated confirmation message.")
    contact_name = models.CharField(max_length=30, blank=True,
        help_text="If you want to display a custom link-text for your contact details, give it "
            "here.")
    contact_verified = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.domain

    def verify(self):        
        # perform various checks:
        client_hosts = self.report.verify_srv_client()
        self.features.check_ipv6(client_hosts)
        client_hosts, stream_features = self.report.verify_client_online(
            client_hosts, ipv6=self.features.has_ipv6)
        
        server_hosts = self.report.verify_srv_server()
        server_hosts = self.report.verify_server_online(server_hosts, ipv6=self.features.has_ipv6)
        
        if self.ssl_port:
            self.features.has_ssl = True
            # NOTE: we take the domain here, since there is no SRV record for SSL
            self.report.verify_ssl(client_hosts, self.ca, self.ssl_port, ipv6=self.features.has_ipv6)
        else: # no ssl port specified
            self.features.has_ssl = False
            self.report.ssl_cert = True # ssl_cert is not a problem if we do not have ssl
            
        if 'starttls' in stream_features:
            self.features.has_tls = True
        else:
            self.features.has_tls = False
            
        if 'register' in stream_features:
            self.features.has_ibr = True
        else:
            self.features.has_ibr = False
            
        if 'plain' in stream_features:
            self.features.has_plain = True
        else:
            self.features.has_plain = False
        
        # save server and its report:
        if self.report.has_problems():
            self.verified = False
        else:
            self.verified = True
        self.features.save()
        self.report.save()
        self.save()
    
    def get_country(self):
        if settings.DATABASES['default']['ENGINE'] == 'django.contrib.gis.db.backends.mysql':
            countries = WorldBorders.objects.filter(geom__intersects=self.location)
            country = [c for c in countries if c.geom.contains(self.location)][0]
        else:
            country = WorldBorders.objects.get(geom__intersects=self.location)
        return country
    
    def get_website(self):
        if self.website:
            return self.website
        else:
            return 'http://%s' % self.domain
        
    def get_contact_text(self):
        if self.contact_name:
            return self.contact_name
        return self.contact