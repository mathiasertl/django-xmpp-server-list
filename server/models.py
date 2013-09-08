# -*- coding: utf-8 -*-
#
# This file is part of xmpplist (https://list.jabber.at).
#
# xmpplist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppllist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmpplist.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import socket
import ssl

from xml.etree import ElementTree

import dns.resolver
import pygeoip

from django.db import models
from django.conf import settings

from django.contrib.auth.models import User

logger = logging.getLogger('xmpplist.server')
geoip = pygeoip.GeoIP(
    os.path.join(settings.GEOIP_CONFIG_ROOT, 'GeoLiteCity.dat'),
    pygeoip.MEMORY_CACHE
)
LOG_TYPE_MODERATION = 1
LOG_TYPE_VERIFICATION = 2
LOG_TYPE_WARNING = 3
LOG_TYPE_INFO = 4

LOG_MESSAGES = {
    'srv-client': 'No xmpp-client SRV-records where found for this server.<br>'
    'Note that if this check fails, some successive tests are skipped, so '
    'fixing this issue might reveal further problems.',
    'srv-server': 'No xmpp-server SRV-records where found for this server.<br>'
    'Note that if this check fails, some successing tests are skipped, so '
    'fixing this issue might reveal further problems.',
    'client-offline': 'Could not verify client connectivity.<br>'
    'None of the hosts referred to by the xmpp-client SRV records where '
    'found to be online. Note that if you use '
    '<a href="http://en.wikipedia.org/wiki/Round-robin_DNS">round-robin '
    'DNS</a>, each host must be online for an xmpp-client SRV record to '
    'be considered online. The following hosts where checked:',
    'server-offline': 'Could not verify server connectivity.<br>'
    'None of the hosts referred to by the xmpp-server SRV records where '
    'found to be online. Note that if you use '
    '<a href="http://en.wikipedia.org/wiki/Round-robin_DNS">round-robin '
    'DNS</a>, each host must be online for an xmpp-server SRV record to '
    'be considered online. The following hosts where checked:',
    'ssl-offline': 'Could not verify SSL connectivity.<br>'
    'If you do not offer SSL connections, please leave the "SSL port" '
    'field empty. Otherwise you have to specify the correct SSL '
    'certificate authority, or, if you use a self-signed certificate, '
    'specify "other" in that field. If your certificate authority is not '
    'listed, please contact us. The following errors where encountered:',
    'tls-cert': 'Could not verify TLS connectivity.'
    'TLS negotiation failed. You have to specify the correct certificate '
    'authority, or, if you use a self-signed certificate, specify "other" '
    'in that field. If your certificate authority is not listed, please '
    'just contact us. <br>The following error was encountered:',

    # warnings:
    'hosts-offline': 'An error was encountered connecting to the following '
    'hosts:',

    # info
    'no-ipv6': 'No IPv6 records were found for at least one SRV record.',
}


def get_addr_str(af, args, hostname):
    if af == socket.AF_INET:
        return '%s:%s (%s)' % (args[0], args[1], hostname)
    elif af == socket.AF_INET6:
        return '[%s]:%s (%s)' % (args[0], args[1], hostname)


def wrap_socket(s, ca):
    if ca.certificate:
        kwargs = {'cert_reqs': ssl.CERT_REQUIRED, 'ca_certs': ca.certificate}
    else:
        kwargs = {'cert_reqs': ssl.CERT_NONE}

    return ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1, **kwargs)


def html_list(l):
    return '<ul><li>%s</li></ul>' % '</li><li>'.join(l)


def get_hosts(host, port, ipv4=True, ipv6=True):
    hosts = []

    try:
        if ipv4 and settings.USE_IP4:
            hosts += socket.getaddrinfo(host, port, socket.AF_INET,
                                        socket.SOCK_STREAM)
    except Exception:
        pass

    try:
        if ipv6 and settings.USE_IP6:
            hosts += socket.getaddrinfo(host, port, socket.AF_INET6,
                                        socket.SOCK_STREAM)
    except Exception:
        pass

    return hosts


class CertificateAuthority(models.Model):
    name = models.CharField(max_length=30, unique=True)
    website = models.URLField(unique=True)
    certificate = models.FilePathField(path=settings.CERTIFICATES_PATH,
                                       null=True, blank=True)

    def __unicode__(self):
        return self.name


class ServerSoftware(models.Model):
    name = models.CharField(max_length=16)
    website = models.URLField()
    newest_version = models.CharField(max_length=8)

    def __unicode__(self):
        return self.name


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

        This test succeeds if all servers returned by the xmpp-client lookup
        have a AAAA record.
        """
        if self.server.failed('srv-client'):
            self.has_ipv6 = False
            return self.has_ipv6

        self.has_ipv6 = True
        for hostname, port, priority in servers:
            try:
                if not get_hosts(hostname, port, ipv4=False, ipv6=True):
                    self.has_ipv6 = False
                    self.server.log(
                        'no-ipv6', msg='%s has no IPv6 record.' % hostname,
                        typ=LOG_TYPE_INFO)
                    break
            except Exception as e:
                msg = 'An error occured while checking IPv6 records for %s: %s' % (hostname, e)
                self.server.log('no-ipv6', msg=msg, typ=LOG_TYPE_INFO)
                self.has_ipv6 = False
                break

        return self.has_ipv6


class Server(models.Model):
    class Meta:
        permissions = (
            ('moderate', 'can moderate servers'),
        )

    # basic information:
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='servers')
    added = models.DateField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    launched = models.DateField(help_text="When the server was launched.")
    city = models.CharField(
        default='', null=True, blank=True, max_length=100,
        help_text="City the server is located in.")
    country = models.CharField(
        default='', null=True, blank=True, max_length=100,
        help_text="Country the server is located in.")

    # information about the service:
    domain = models.CharField(
        unique=True, max_length=60,
        help_text="The primary domain of your server.")
    website = models.URLField(
        blank=True, help_text="A homepage where one can find information on "
        "your server. If left empty, the default is http://<domain>.")
    ca = models.ForeignKey(
        CertificateAuthority, related_name='servers', verbose_name='CA',
        help_text="The Certificate Authority of the certificate used in "
        "SSL/TLS connections.")
    ssl_port = models.PositiveIntegerField(
        default=5223, blank=True, null=True, verbose_name='SSL port',
        help_text="The Port where your server allows SSL connections. Leave "
        "empty if your server does not allow SSL connections.")

    # verification
    verified = models.NullBooleanField(default=None)

    # moderation:
    moderated = models.NullBooleanField(default=None)
    features = models.OneToOneField(Features, related_name='server')

    # queried information
    software = models.ForeignKey(ServerSoftware, related_name='servers',
                                 null=True, blank=True)
    software_version = models.CharField(max_length=30, blank=True)

    # contact information
    CONTACT_TYPE_CHOICES = (
        ('M', 'MUC'),
        ('J', 'JID'),
        ('E', 'e-mail'),
        ('W', 'website'),
    )
    contact = models.CharField(
        max_length=60,
        help_text="The address where the server-admins can be reached.")
    contact_type = models.CharField(
        max_length=1, choices=CONTACT_TYPE_CHOICES, default='J',
        help_text="What type your contact details are. This setting will "
        "affect how the contact details are rendered on the front page. If "
        "you choose a JID or an e-mail address, you will receive an automated "
        "confirmation message.")
    contact_name = models.CharField(
        max_length=60, blank=True,
        help_text="If you want to display a custom link-text for your contact "
        "details, give it here.")
    contact_verified = models.BooleanField(default=False)

    def __unicode__(self):
        return self.domain

    def check_hostname(self, hostname, port, ssl=False, tls=False,
                       features=False, xmlns='jabber:client'):
        """
        Returns True if all addresses for the given host are reachable on the
        given port.

        :param hostname: A hostname specified by an SRV record.
        :param     port: A port specified by an SRV record.
        :param   domain: If given, XML stream features will be checked.
        :param    xmlns: The XML stream namespace used if XML stream features
            are checked
        """
        logger.debug('Verify connectivity for %s %s', hostname, port)
        myfeatures = set()
        hosts = get_hosts(hostname, port)
        if not hosts:
            raise RuntimeError(
                "%s: No hosts returned by DNS lookup" % hostname)

        first_iter = True
        for af, socktype, proto, canonname, connect_args in hosts:
            if af == socket.AF_INET:
                addr_str = '%s:%s (%s)' % (connect_args[0], connect_args[1],
                                           hostname)
            elif af == socket.AF_INET6:
                addr_str = '[%s]:%s (%s)' % (connect_args[0], connect_args[1],
                                             hostname)

            try:
                s = socket.socket(af, socktype, proto)
                s.settimeout(1.0)
                s.connect(connect_args)

                if ssl:  # wrap SSL if requested
                    s = wrap_socket(s, self.ca)

                if features:
                    sock_features = self.get_stream_features(s, xmlns)
                    if first_iter:
                        myfeatures = sock_features
                        first_iter = False
                    else:
                        myfeatures &= sock_features

                s.close()
            except RuntimeError as e:
                raise e
            except Exception as e:
                raise RuntimeError('Failed to connect to %s (%s): %s'
                                   % (addr_str, hostname, e))

        return myfeatures

    def get_stream_features(self, sock, xmlns='jabber:client'):
        """
        <stream:stream
                xmlns='jabber:client'
                xmlns:stream='http://etherx.jabber.org/streams'
                id='00a5101e-4e49-43b8-8449-670a862d33f7'
                from='gajim.org'
                version='1.0'
                xml:lang='en'>
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
                to='%s' version='1.0'>""" % (xmlns, self.domain)
            sock.send(msg.encode('utf-8'))
            resp = sock.recv(4096).decode('utf-8')
            if not resp:  # happens at sternenschweif.de
                raise RuntimeError(
                    '%s: No answer received during stream negotiation.'
                    % self.domain)
            if '<stream:error>' in resp:
                raise RuntimeError(
                    '%s: Received error during stream negotiation.'
                    % self.domain)

            i = 0
            while not resp.endswith('</stream:features>') and i < 10:
                resp += sock.recv(4096).decode('utf-8')
                i += 1

            elem = ElementTree.fromstring(resp + '</stream:stream>')
            elem = elem.find('{http://etherx.jabber.org/streams}features')

            starttls = elem.find('{urn:ietf:params:xml:ns:xmpp-tls}starttls')
            if starttls is not None:
                features.add('starttls')

            stanza = '{urn:ietf:params:xml:ns:xmpp-tls}required'
            if starttls is None or starttls.find(stanza) is None:
                features.add('plain')

            stanza = '{http://jabber.org/features/iq-register}register'
            if elem.find(stanza) is not None:
                features.add('register')

            if 'starttls' in features and not self.failed('tls-cert'):
                try:
                    stanza = "<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>"
                    sock.send(stanza.encode('utf-8'))
                    sock.recv(4096).decode('utf-8')
                    sock = wrap_socket(sock, self.ca)
                except Exception as e:
                    peer = sock.getpeername()
                    addr, port = peer[0], peer[1]
                    self.fail(
                        'tls-cert',
                        '<ul><li>%s, port %s: %s</li></ul>' % (addr, port, e))

            # close stream again:
            sock.send('</stream:stream>'.encode('utf-8'))
            sock.recv(4096)
        except Exception as e:
            logger.error('%s: Exception while getting stream features: %s',
                         self.domain, e)

        return features

    def srv_lookup(self, service, proto='tcp'):
        """
        Function for doing SRV-lookups. Returns a list of host/port tuples for
        the given srv-record.
        """
        record = '_%s._%s.%s' % (service, proto, self.domain)
        try:
            resolver = dns.resolver.Resolver()
            resolver.lifetime = 3.0
            answers = resolver.query(record, 'SRV')
        except:
            return []
        hosts = []
        for answer in answers:
            hosts.append((answer.target.to_text(True), answer.port,
                          answer.priority))
        return sorted(hosts, key=lambda host: host[2])

    def verify_srv_client(self):
        """
        Verify xmpp-client SRV records.

        This test succeeds if the 'xmpp-client' SRV record has one or more
        entries.
        """
        hosts = self.srv_lookup('xmpp-client')
        if not hosts:
            self.fail('srv-client')

        return hosts

    def verify_srv_server(self):
        """
        Verify xmpp-server SRV records.

        This test succeeds if the 'xmpp-server' SRV record has one or more
        entries.
        """
        hosts = self.srv_lookup('xmpp-server')
        if not hosts:
            self.fail('srv-server')

        return hosts

    def verify_client_online(self, records):
        """
        Verify that at least one of the hosts referred to by the xmpp-client
        SRV records is currently online.
        """
        errors, online, features = [], [], set()
        if self.failed('srv-client') or not records:
            return online, features

        for hostname, port, priority in records:
            try:
                myfeatures = self.check_hostname(hostname, port, tls=True,
                    features=True)
            except RuntimeError as e:
                errors.append(str(e))
                continue

            if online:
                features &= myfeatures
            else:  # first online host
                features = myfeatures

            online.append((hostname, port, priority))

        if 'starttls' not in features:
            self.fail('tls-cert')

        if not online:  # not online, append errors to 'client-offline' message
            self.fail('client-offline', msg=html_list(errors))
        elif errors:  # only some hosts are offline, so this is only a warning
            self.log('hosts-offline', msg=html_list(errors),
                     typ=LOG_TYPE_WARNING)

        return online, features

    def verify_server_online(self, hosts):
        """
        Verify that at least one of the hosts referred to by the xmpp-server
        SRV records is currently online.
        """
        online, errors = [], []
        if self.failed('srv-server') or not hosts:
            return online

        for host in hosts:
            try:
                self.check_hostname(host[0], host[1])
            except RuntimeError as e:
                errors.append(str(e))
                continue

            online.append(host)

        if not online:  # not online, append errors to 'server-online' message
            self.fail('server-offline', msg=html_list(errors))
        elif errors:  # only some hosts are offline, so this is only a warning
            self.log('hosts-offline', msg=html_list(errors),
                     typ=LOG_TYPE_WARNING)

        return online

    def verify_ssl(self, hosts):
        """Verify SSL connectivity.

        This check receives only the hosts returned by verify_client_online
        and, unlike that method, fails if only one of the connections fails
        (since all hosts are assumed to be in fact online.)
        """
        self.ssl_cert = True
        online, errors = [], []
        for host, port, priority in hosts:
            try:
                self.check_hostname(host, int(self.ssl_port), ssl=True)
                online.append(host)
            except RuntimeError as e:
                errors.append(str(e))

        if errors:
            self.fail('ssl-offline', msg=html_list(errors))

    @property
    def location(self):
        if not self.city or not self.country:
            return 'Unknown'
        else:
            return '%s/%s' % (self.city, self.country)


    def set_location(self, hostname):
        try:
            data = geoip.record_by_name(hostname)
            self.city = data['city']
            self.country = data['country_name']
        except Exception:
            self.city = ''
            self.countr = ''

    def verify(self):
        self.verified = False
        self.logentries.all().delete()

        # perform various checks:
        client_srv = self.verify_srv_client()
        client_hosts, stream_features = self.verify_client_online(client_srv)

        server_srv = self.verify_srv_server()
        self.verify_server_online(server_srv)

        if client_hosts:  # use first online client host if available
            self.set_location(client_hosts[0][0])
        elif client_srv:  # use other srv-record otherwise
            self.set_location(client_srv[0][0])
        else:  # no way to query location - reset!
            self.city = ''
            self.country = ''

        if self.ssl_port:
            self.features.has_ssl = True
            self.verify_ssl(client_hosts)
        else:  # no ssl port specified
            self.features.has_ssl = False

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

        self.features.save()
        self.save()

    def get_website(self):
        if self.website:
            return self.website
        else:
            return 'http://%s' % self.domain

    def get_contact_text(self):
        if self.contact_name:
            return self.contact_name
        return self.contact

    def fail(self, key, msg='', typ=LOG_TYPE_VERIFICATION):
        logger.debug('%s: %s' % (key, msg))
        self.logentries.create(key=key, msg=msg, typ=typ)

    def failed(self, key):
        return self.logentries.filter(key=key).exists()

    def passed(self, key):
        return self.failed(key)

    def log(self, key, msg='', typ=LOG_TYPE_WARNING):
        self.logentries.create(key=key, msg=msg, typ=typ)

    def get_moderations(self):
        return self.logentries.filter(typ=LOG_TYPE_MODERATION)

    def get_verifications(self):
        return self.logentries.filter(typ=LOG_TYPE_VERIFICATION)

    def get_warnings(self):
        return self.logentries.filter(typ=LOG_TYPE_WARNING)

    def get_infos(self):
        return self.logentries.filter(typ=LOG_TYPE_INFO)

    def do_contact_verification(self):
        typ = self.contact_type

        # Set contact_verified if it sthe same as your email or JID:
        if typ == 'E' and self.user.email == self.contact \
                and self.user.email_confirmed:
            self.contact_verified = True
        elif typ == 'J' and self.user.jid == self.contact \
                and self.user.jid_confirmed:
            self.contact_verified = True
        elif typ in ['J', 'E']:
            key = self.confirmations.create(subject=self)
            key.send()

    def save(self, *args, **kwargs):
        if self.verified is not None:
            qs = self.logentries.filter(typ=LOG_TYPE_VERIFICATION)
            self.verified = not qs.exists()
        return super(Server, self).save(*args, **kwargs)


class LogEntry(models.Model):
    LOG_TYPE_CHOICES = (
        (LOG_TYPE_MODERATION, 'moderation'),
        (LOG_TYPE_VERIFICATION, 'verification'),
        (LOG_TYPE_WARNING, 'warning'),
        (LOG_TYPE_INFO, 'info'),
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    typ = models.IntegerField(choices=LOG_TYPE_CHOICES)
    key = models.CharField(max_length=16)
    msg = models.TextField(default='', null=True, blank=True)

    server = models.ForeignKey(Server, related_name='logentries')

    def get_info(self):
        return LOG_MESSAGES[self.key]

    def __unicode__(self):
        if self.typ == LOG_TYPE_MODERATION:
            type = 'MODE'
        elif self.typ == LOG_TYPE_VERIFICATION:
            type = 'VERI'
        elif self.typ == LOG_TYPE_WARNING:
            type = 'WARN'
        elif self.typ == LOG_TYPE_INFO:
            type = 'INFO'

        return '%s - %s: %s' % (self.server.domain, type, self.key)
