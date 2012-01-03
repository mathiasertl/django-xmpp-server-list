import socket

import dns.resolver

from django.db import models
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

from xmpplist.world.models import WorldBorders

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
    srv_client = models.BooleanField(default=False)
    srv_server = models.BooleanField(default=False)
    
    client_offline = models.BooleanField(default=False)
    server_offline = models.BooleanField(default=False)
    
    def has_problems(self):
        return self.srv_client or self.srv_server \
            or self.client_offline or self.server_offline
    
    def __unicode__(self):
        condition = 'ok'
        if self.has_problems():
            condition = 'has problems'
        return 'Report on %s: %s' % ('domain', condition)

class Server(models.Model):
    class Meta:
        permissions = (
            ('moderate', 'can moderate servers'),
        )
        
    # basic information:
    user = models.ForeignKey(User, related_name='servers')
    added = models.DateField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    launched = models.DateField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    
    # information about the service:
    domain = models.CharField(unique=True, max_length=30)
    website = models.URLField()
    ca = models.ForeignKey(CertificateAuthority, related_name='servers')
    
    # verification
    moderated = models.NullBooleanField(default=None)
    verified = models.NullBooleanField(default=None)
    report = models.OneToOneField(ServerReport, related_name='server')
    
    # queried information
    software = models.ForeignKey(ServerSoftware, related_name='servers', blank=True, null=True)
    software_version = models.CharField(max_length=16, blank=True, null=True)
    
    support_plain = models.NullBooleanField(default=None)
    support_ssl = models.NullBooleanField(default=None)
    ssl_port = models.PositiveIntegerField(default=5223, blank=True, null=True)
    support_tls = models.NullBooleanField(default=None)
    
    # contact information
    CONTACT_TYPE_CHOICES=(
        ('M', 'MUC'),
        ('J', 'JID'),
        ('E', 'e-mail'),
        ('W', 'website'),
    )
    contact = models.CharField(max_length=30)
    contact_name = models.CharField(max_length=30)
    contact_type = models.CharField(max_length=1, choices=CONTACT_TYPE_CHOICES)
    
    def __unicode__(self):
        return self.domain
    
    def srv_lookup(self, service, proto='tcp'):
        """
        Function for doing SRV-lookups. Returns a list of host/port tuples for
        the given srv-record.
        """
        record = '_%s._%s.%s' % (service, proto, self.domain)
        try:
            answers = dns.resolver.query(record, 'SRV')
        except:
            return []
        hosts = []
        for answer in answers:
            hosts.append((answer.target.to_text(True), answer.port, answer.priority))
        return sorted(hosts, key=lambda host: host[2])
        
    def check_host(self, host, port):
        s = socket.socket()
        s.settimeout(3.0)
        try:
            s.connect( (host, port) )
            s.close()
            return True
        except: 
            return False
        
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

    def verify(self):
        report = ServerReport()
        
        # do SRV lookups
        client_hosts = self.srv_lookup('xmpp-client')
        if not client_hosts:
            report.srv_client = True
        server_hosts = self.srv_lookup('xmpp-server')
        if not server_hosts:
            report.srv_server = True
        
        report.client_offline = True
        for host in client_hosts:
            if self.check_host(host[0], host[1]):
                report.client_offline = False
                break
        
        report.server_offline = True
        for host in server_hosts:
            if self.check_host(host[0], host[1]):
                report.server_offline = False
                break
        
        # udpate this instance:
        if report.has_problems():
            self.verified = False
        else:
            self.verified = True
        report.save()
        old_report = self.report
        self.report = report
        self.save()
        old_report.delete()
            
        return report
    
    def get_country(self):
        p = Point(self.longitude, self.latitude)
        if settings.DATABASES['default']['ENGINE'] == 'django.contrib.gis.db.backends.mysql':
            countries = WorldBorders.objects.filter(geom__intersects=p)
            country = [c for c in countries if c.geom.contains(p)][0]
        else:
            country = WorldBorders.objects.get(geom__intersects=p)
        return country