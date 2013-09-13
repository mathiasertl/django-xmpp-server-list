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

import copy
import logging
import os
import socket

from datetime import datetime

import pygeoip

from django.db import models
from django.conf import settings

from xmpp.clients import StreamFeatureClient

from server.dns import srv_lookup
from server.dns import lookup
from server.managers import ServerManager

log = logging.getLogger(__name__)
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


class Server(models.Model):
    class Meta:
        permissions = (
            ('moderate', 'can moderate servers'),
        )
    objects = ServerManager()

    # basic information:
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='servers')
    added = models.DateField(auto_now_add=True)
    last_seen = models.DateField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    launched = models.DateField(help_text="When the server was launched.")

    # geolocation:
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

    # SSL/TLS verification
    c2s_tls_verified = models.BooleanField(default=True)
    c2s_ssl_verified = models.BooleanField(default=True)
    s2s_tls_verified = models.BooleanField(default=True)

    # DNS-related information:
    c2s_srv_records = models.BooleanField(default=False)
    s2s_srv_records = models.BooleanField(default=False)
    ipv6 = models.BooleanField(default=False)

    # c2s stream features:
    c2s_auth = models.BooleanField(default=False)  # Non-SASL authentication
    c2s_caps = models.BooleanField(default=False)
    c2s_compression = models.BooleanField(default=False)
    c2s_register = models.BooleanField(default=False)  # In-Band registration
    c2s_rosterver = models.BooleanField(default=False)  # obsolete
    c2s_sasl_auth = models.BooleanField(default=False)
    c2s_starttls = models.BooleanField(default=False)
    c2s_starttls_required = models.BooleanField(default=False)

    # s2s stream features:
    s2s_starttls = models.BooleanField(default=False)
    s2s_starttls_required = models.BooleanField(default=False)
    s2s_caps = models.BooleanField(default=False)

    # contact information
    CONTACT_TYPE_CHOICES = (
        ('M', 'MUC'),
        ('J', 'JID'),
        ('E', 'e-mail'),
        ('W', 'website'),
    )
    C2S_STREAM_FEATURES = [
        'auth',
        'caps',
        'compression',
        'register',
        'rosterver',
        'sasl_auth',
        'starttls',
    ]
    S2S_STREAM_FEATURES = [
        'caps',
        'starttls',
    ]
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

    def verify_srv_client(self):
        """
        Verify xmpp-client SRV records.

        This test succeeds if the 'xmpp-client' SRV record has one or more
        entries.
        """
        hosts = srv_lookup(self.domain, 'xmpp-client')
        if hosts:
            self.c2s_srv_records = True
        else:
            self.c2s_srv_records = False

        return hosts

    def verify_srv_server(self):
        """
        Verify xmpp-server SRV records.

        This test succeeds if the 'xmpp-server' SRV record has one or more
        entries.
        """
        hosts = srv_lookup(self.domain, 'xmpp-server')
        if hosts:
            self.s2s_srv_records = True
        else:
            self.s2s_srv_records = False

        return hosts

    @property
    def location(self):
        if not self.city and not self.country:
            return 'Unknown'
        elif self.country:
            return self.country
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

    def _merge_features(self, new, kind, ssl=False):
        attr = '_%s_stream_features' % kind
        old = getattr(self, attr)
        if old is None:
            setattr(self, attr, copy.deepcopy(new))
            return new

        if ssl and 'starttls' in old:
            # fake starttls stanza on legacy SSL so merging works
            new['starttls'] = old['starttls']

        if old != new:
            # This host does not deliver the exact same stream features as a
            # previous host. We modify the features to only include the
            # features common to both hosts.
            log.error("%s: Differing stream features found.", self.domain)

            for key in set(new.keys()) - set(old.keys()):
                # remove new keys found in new but not in old features
                del new[key]

            if 'starttls' in new:  # handle starttls required field
                old_req = old['starttls']['required']
                new_req = new['starttls']['required']
                if not old_req and new_req:
                    new['starttls']['required'] = False

            if new['compression']:
                meths = set(new['compression']['methods'])
                old_meths = set(old['compression']['methods'])
                new['compression']['methods'] = list(meths | old_meths)
            if new['sasl_auth']:
                mechs = set(new['sasl_auth']['mechanisms'])
                old_mechs = set(old['sasl_auth']['mechanisms'])
                new['sasl_auth']['mechanisms'] = list(mechs | old_mechs)

        setattr(self, attr, copy.deepcopy(new))
        return new

    def _c2s_stream_feature_cb(self, host, port, features, ssl, tls):
        log.info('Stream Features: %s:%s: %s', host, port,
                 sorted(features.keys()))
        self._c2s_online.add((host, port))
        self.last_seen = datetime.now()  # we saw an online host

        features = self._merge_features(features, 'c2s', ssl)

        self.c2s_starttls_required = features.get(
            'starttls', {}).get('required', False)
        for key in self.C2S_STREAM_FEATURES:
            setattr(self, 'c2s_%s' % key, key in features)
            features.pop(key, None)

        if features:
            log.debug('%s: Unhandled features: %s', self.domain, features)

    def _c2s_cert_invalid(self, host, port, ssl, tls):
        log.error('Invalid SSL certificate: %s:%s (ssl=%s, tls=%s)',
                  host, port, ssl, tls)
        if ssl:
            self.c2s_ssl_verified = False
        else:
            self.c2s_tls_verified = False

    def _s2s_stream_feature_cb(self, host, port, features, ssl, tls):
        log.info('Stream Features: %s:%s: %s', host, port,
                 sorted(features.keys()))
        self._s2s_online.add((host, port))

        features = self._merge_features(features, 's2s')

        self.s2s_starttls_required = features.get(
            'starttls', {}).get('required', False)
        for key in self.S2S_STREAM_FEATURES:
            setattr(self, 's2s_%s' % key, key in features)
            features.pop(key, None)

        if features:
            log.debug('%s: Unhandled features: %s', self.domain, features)

    def _s2s_cert_invalid(self, host, port, ssl, tls):
        log.error('Invalid SSL certificate: %s:%s')
        self.s2s_tls_verified = False

    def verify_ipv6(self, hosts):
        self.ipv6 = True
        try:
            for host in set(hosts):
                if not lookup(host, ipv4=False):
                    self.ipv6 = False
                    return
        except:
            self.ipv6 = False

    def verify(self):
        self._c2s_online = set()  # list of online c2s SRV records
        self._s2s_online = set()  # list of online s2s SRV records
        self._c2s_stream_features = None  # private var for stream feature checking
        self._s2s_stream_features = None  # private var for stream feature checking

        # set the default to True, error callbacks will set to false on error
        self.c2s_ssl_verified = True
        self.c2s_tls_verified = True
        self.s2s_tls_verified = True

        self.verified = False
        self.logentries.all().delete()

        # verify c2s-connections
        client_srv = self.verify_srv_client()
        for domain, port, prio in client_srv:
            client = StreamFeatureClient(
                domain=self.domain,
                callback=self._c2s_stream_feature_cb,
                cert=self.ca.certificate,
                cert_errback=self._c2s_cert_invalid
            )
            client.connect(domain, port)
            client.process(block=True)

        # verify legacy SSL connections
        if self.ssl_port:
            for host in list(self._c2s_online):
                client = StreamFeatureClient(
                    domain=self.domain,
                    callback=self._c2s_stream_feature_cb,
                    cert=self.ca.certificate,
                    cert_errback=self._c2s_cert_invalid
                )
                client.connect(host[0], self.ssl_port,
                               use_tls=False, use_ssl=True)
                client.process(block=True)

        # verify s2s connections
        server_srv = self.verify_srv_server()
        for domain, port, prio in server_srv:
            client = StreamFeatureClient(
                domain=self.domain,
                callback=self._s2s_stream_feature_cb,
                cert=self.ca.certificate,
                cert_errback=self._s2s_cert_invalid,
                ns='jabber:server',
            )
            client.connect(domain, port)
            client.process(block=True)

        # get location:
        if self._c2s_online:
            self.set_location(list(self._c2s_online)[0])
        elif client_srv:  # get location
            self.set_location(client_srv[0][0])
        else:  # no way to query location - reset!
            self.city = ''
            self.country = ''

        # check IPv6 DNS records:
        self.verify_ipv6([r[0] for r in client_srv + server_srv])

        # If my CA has no certificates (the "other" ca), no certificates were
        # actually verified, so set them to false manually.
        if not self.ca.certificate:
            self.c2s_ssl_verified = False
            self.c2s_tls_verified = False
            self.s2s_tls_verified = False

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
        log.debug('%s: %s' % (key, msg))
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

    def automatic_verification(self):
        if self.contact_type in ['J', 'E'] and not self.contact_verified:
            return True
        return False

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
