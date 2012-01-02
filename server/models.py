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
    created = models.DateField(auto_now_add=True)
    srv_client = models.BooleanField(default=False)
    srv_server = models.BooleanField(default=False)

class Server(models.Model):
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
    moderated = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
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
        answers = dns.resolver.query(record, 'SRV')
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

    def report(self):
        client_hosts = self.srv_lookup('xmpp-client')
        server_hosts = self.srv_lookup('xmpp-server')
        report = Report(server=self,
                        client_online_max=len(client_hosts),
                        server_online_max=len(server_hosts)
        )
        
        client_hosts_available = 0
        for host in client_hosts:
            if self.check_host(host[0], host[1]):
                client_hosts_available += 1
        report.client_online = client_hosts_available
                
        server_hosts_available = 0
        for host in server_hosts:
            if self.check_host(host[0], host[1]):
                server_hosts_available += 1
        report.server_online = server_hosts_available
        
        report.save()
        return report
    
    def get_country(self):
        p = Point(self.longitude, self.latitude)
        if settings.DATABASES['default']['ENGINE'] == 'django.contrib.gis.db.backends.mysql':
            countries = WorldBorders.objects.filter(geom__intersects=p)
            country = [c for c in countries if c.geom.contains(p)][0]
        else:
            country = WorldBorders.objects.get(geom__intersects=p)
        return country
        
    
class Report(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    
    client_online = models.IntegerField(default=0)
    client_online_max = models.IntegerField()
    server_online = models.IntegerField(default=0)
    server_online_max = models.IntegerField()
    
    ssl_online = models.BooleanField(default=False)
    
    server = models.ForeignKey(Server)