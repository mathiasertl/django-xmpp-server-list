import socket

import dns.resolver

#from django.db import models
from django.contrib.gis.db import models
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

from xmpplist.world.models import WorldBorders

def dns_lookup(self, record, record_type):
    try:
        print('DIG %s %s' % (record_type, record))
        return dns.resolver.query(record, record_type)
    except:
        return []

def check_host(host, port, ipv6=False):
    if ipv6:
        hosts = socket.getaddrinfo(host, port, socket.AF_INET6, socket.SOCK_STREAM)
    else:
        hosts = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)

    for af, socktype, proto, canonname, connect_args in hosts:
        try:
            s = socket.socket(af, socktype, proto)
            s.settimeout(1.0)
            print('connect: %s %s' % (connect_args[0], connect_args[1]))
            s.connect(connect_args)
            s.close()
        except: 
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
            answers = dns.resolver.query(record, 'SRV')
        except:
            return []
        hosts = []
        for answer in answers:
            hosts.append((answer.target.to_text(True), answer.port, answer.priority))
        return sorted(hosts, key=lambda host: host[2])
        
    def check_host_ssl(self, host, port):
        try:
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(self.domain, self.ssl_port)
            ssl_sock = ssl.wrap_socket( s,
                ssl_version=ssl.PROTOCOL_TLSv1,
                    cert_reqs=ssl.CERT_REQUIRED,
                    ca_certs=opts.ca_cert )
            ssl_sock.close()
            return True
        except socket.timeout:
                print( 'closed.' )
        except ssl.SSLError as e:
                print( 'Open, but SSL negotiation failed: %s'%(e.args[1]) )
        except Exception as e:
                print( "Open, but SSL negotiation failed." )

    def verify_srv_client(self):
        """
        Verify xmpp-client SRV records.
        """
        hosts = self.srv_lookup('xmpp-client')
        if not hosts:
            self.srv_client = False
        return hosts
            
    def verify_srv_server(self):
        """
        Verify xmpp-server SRV records.
        """
        hosts = self.srv_lookup('xmpp-server')
        if not hosts:
            self.srv_server = False
        return hosts
            
    def verify_client_online(self, hosts):
        """
        Verify that at least one of the hosts referred to by the xmpp-client SRV records is
        currently online.
        """
        if not self.srv_client:
            return
        
        self.client_online = False
        for host in hosts:
            if check_host(host[0], host[1]):
                self.client_online = True
                break
            
    def verify_server_online(self, hosts):
        """
        Verify that at least one of the hosts referred to by the xmpp-server SRV records is
        currently online.
        """
        if not self.srv_server:
            return
        
        self.server_online = False
        for host in hosts:
            if check_host(host[0], host[1]):
                self.server_online = True
                break
    
    def is_ok(self):
        return self.srv_client and self.srv_server and self.client_online and self.server_online \
            and self.ssl_cert and self.tls_cert
    
    def has_problems(self):
        return not self.is_ok()
    
    def __unicode__(self):
        condition = 'ok'
        if self.has_problems():
            condition = 'has problems'
        return 'Report on %s: %s' % ('domain', condition)

class Features(models.Model):
    # connection-related:
    has_plain = models.BooleanField(default=False)
    has_ssl = models.BooleanField(default=False)
    has_tls = models.BooleanField(default=False)
    has_ipv6 = models.BooleanField(default=False)
    
    # features:
    has_muc = models.BooleanField(default=False)
    has_irc = models.BooleanField(default=False)
    has_vcard = models.BooleanField(default=False)
    has_pep = models.BooleanField(default=False)
    has_proxy = models.BooleanField(default=False)
    has_webpresence = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.server.domain
    
    def check_ipv6(self, hosts):
        if not self.server.report.srv_client:
            return
        
        for host in hosts:
            if check_host(host[0], host[1], ipv6=True):
                self.has_ipv6 = True
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
    moderated = models.NullBooleanField(default=None)
    report = models.OneToOneField(ServerReport, related_name='server')
    
    # moderation:
    verified = models.NullBooleanField(default=None)
    features = models.OneToOneField(Features, related_name='server')
    
    # queried information
    software = models.ForeignKey(ServerSoftware, related_name='servers', blank=True)
    software_version = models.CharField(max_length=16, blank=True)
    
    objects = models.GeoManager()
    
    # contact information
    CONTACT_TYPE_CHOICES=(
        ('M', 'MUC'),
        ('J', 'JID'),
        ('E', 'e-mail'),
        ('W', 'website'),
    )
    contact = models.CharField(max_length=30, blank=True,
        help_text="The address where the server-admins can be reached. If left empty, your "
            "personal JID will be used.")
    contact_type = models.CharField(max_length=1, choices=CONTACT_TYPE_CHOICES, default='J',
        blank=True,
        help_text="What type your contact details are. This setting will affect how the contact "
            "details are rendered on the front page. This setting is not used if you leave the "
            "next field empty.")
    contact_name = models.CharField(max_length=30, blank=True,
        help_text="If you want to display a custom link-text for your contact details, give it "
            "here.")
    
    def __unicode__(self):
        return self.domain

    def verify(self):        
        # perform various checks:
        client_hosts = self.report.verify_srv_client()
        server_hosts = self.report.verify_srv_server()
        self.report.verify_client_online(client_hosts)
        self.report.verify_server_online(server_hosts)
        
        self.features.check_ipv6(client_hosts)
        
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
        print(self.website)
        if self.website:
            return self.website
        else:
            return 'http://%s' % self.domain
        
    def get_contact_text(self):
        if self.contact_name:
            return self.contact_name
        elif self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.username