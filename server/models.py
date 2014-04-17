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

from __future__ import with_statement

import copy
import logging
import os

from datetime import datetime

import pygeoip

from django.db import models
from django.conf import settings

from xmpp.clients import StreamFeatureClient

from server.constants import CONTACT_TYPE_CHOICES
from server.constants import C2S_STREAM_FEATURES
from server.constants import S2S_STREAM_FEATURES
from server.dns import srv_lookup
from server.dns import lookup
from server.managers import ServerManager

log = logging.getLogger(__name__)
geoip = pygeoip.GeoIP(
    os.path.join(settings.GEOIP_CONFIG_ROOT, 'GeoLiteCity.dat'),
    pygeoip.MEMORY_CACHE
)

import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds, client):
    def signal_handler(signum, frame):
        client.disconnect(wait=False, send_close=False, reconnect=False)
        raise TimeoutException()
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class CertificateAuthority(models.Model):
    name = models.CharField(max_length=30, unique=True)
    website = models.URLField(unique=True)
    certificate = models.FilePathField(path='core/static/certs',
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


class LogEntry(models.Model):
    CONDITIONS = (
        (logging.CRITICAL, logging.getLevelName(logging.CRITICAL)),
        (logging.ERROR, logging.getLevelName(logging.ERROR)),
        (logging.WARNING, logging.getLevelName(logging.WARNING)),
        (logging.INFO, logging.getLevelName(logging.INFO)),
        (logging.DEBUG, logging.getLevelName(logging.DEBUG)),
    )
    server = models.ForeignKey('Server', related_name='logs')
    level = models.PositiveSmallIntegerField(choices=CONDITIONS)
    message = models.TextField()

    @property
    def critical(self):
        return self.level == logging.CRITICAL

    @property
    def error(self):
        return self.level == logging.ERROR

    @property
    def warning(self):
        return self.level == logging.WARNING

    @property
    def info(self):
        return self.level == logging.INFO

    @property
    def debug(self):
        return self.level == logging.DEBUG


class Server(models.Model):
    class Meta:
        permissions = (
            ('moderate', 'can moderate servers'),
        )
    objects = ServerManager()

    # basic information:
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='servers')
    added = models.DateField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    launched = models.DateField(help_text="When the server was launched.")

    # When the server was last seen online:
    last_seen = models.DateTimeField(null=True, blank=True)

    # When the server was last successfully checked:
    last_checked = models.DateTimeField(null=True, blank=True)

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

    # moderation:
    moderated = models.NullBooleanField(default=None)
    features = models.OneToOneField(Features, related_name='server')

    # queried information
    software = models.ForeignKey(ServerSoftware, related_name='servers',
                                 null=True, blank=True)
    software_version = models.CharField(max_length=30, blank=True)

    # DNS-related information:
    c2s_srv_records = models.BooleanField(default=False)
    s2s_srv_records = models.BooleanField(default=False)
    ipv6 = models.BooleanField(default=False)

    # SSL/TLS verification
    c2s_tls_verified = models.BooleanField(default=False)
    c2s_ssl_verified = models.BooleanField(default=False)
    s2s_tls_verified = models.BooleanField(default=False)

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
    s2s_dialback = models.BooleanField(default=False)

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

    @property
    def verified(self):
        if self.last_seen is None:
            return None
        return self.c2s_srv_records and self.s2s_srv_records \
            and (self.c2s_tls_verified or self.ca.certificate is None) \
            and (self.s2s_tls_verified or self.ca.certificate is None) \
            and self.c2s_starttls

    @verified.setter
    def verified(self, value):
        if not value:
            self.c2s_srv_records = False
            self.s2s_srv_records = False
            self.c2s_tls_verified = False
            self.ca.certificate = False
            self.s2s_tls_verified = False
            self.ca.certificate = False
            self.c2s_starttls = False


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
            log.debug('%s: Differing stream features found.', self.domain)

            oldkeys = set(old.keys())
            newkeys = set(new.keys())

            if oldkeys != newkeys:
                # we strip starttls from output because SSL does not have that
                # stanza and we fake it above.
                self.warn(
                    "Hosts (%s) offer different stream features: %s vs. %s",
                    kind, ', '.join(sorted(oldkeys - {'starttls', })),
                    ', '.join(sorted(newkeys - {'starttls', })))

            for key in set(new.keys()) - set(old.keys()):
                # remove new keys found in new but not in old features
                del new[key]

            if 'starttls' in new:  # handle starttls required field
                old_req = old['starttls']['required']
                new_req = new['starttls']['required']
                if not old_req and new_req:
                    self.error('STARTTLS not required on all hosts.')
                    new['starttls']['required'] = False

            if 'compression' in new:
                meths = set(new['compression']['methods'])
                old_meths = set(old.get('compression', {}).get('methods', []))
                if meths != old_meths:
                    self.warn(
                        'Hosts offer different compression methods: %s vs. %s',
                        ', '.join(sorted(meths)), ', '.join(sorted(old_meths)))
                new['compression']['methods'] = list(meths & old_meths)
            if 'sasl_auth' in new:
                mechs = set(new['sasl_auth']['mechanisms'])
                old_mechs = set(old.get('sasl_auth', {}).get('mechanisms', []))
                if mechs != old_mechs:
                    self.warn(
                        'Hosts offer different SASL auth mechanisms: %s vs. %s',
                        ', '.join(sorted(mechs)),
                        ', '.join(sorted(old_mechs)))
                new['sasl_auth']['mechanisms'] = list(mechs & old_mechs)

        setattr(self, attr, copy.deepcopy(new))
        return new

    def _c2s_stream_feature_cb(self, host, port, features, ssl, tls):
        log.debug('Stream Features: %s:%s: %s', host, port,
                 sorted(features.keys()))
        self._c2s_online.add((host, port))
        self.last_seen = datetime.now()  # we saw an online host

        features = self._merge_features(features, 'c2s', ssl)

        self.c2s_starttls_required = features.get(
            'starttls', {}).get('required', False)
        for key in C2S_STREAM_FEATURES:
            setattr(self, 'c2s_%s' % key, key in features)
            features.pop(key, None)

        if features:
            log.debug('%s: Unhandled features: %s', self.domain, features)

    def _invalid_tls(self, host, port, ssl, tls, ns):
        if ns == 'jabber:client' and ssl:  # c2s using SSL
            self._c2s_ssl_verified = False
        elif ns == 'jabber:client' and tls:  # c2s using TLS
            self._c2s_tls_verified = False
        elif ns == 'jabber:server':  # s2s connection
            self._s2s_tls_verified = False
        else:
            log.error('Unknown namespace: %s', ns)

    def invalid_chain(self, host, port, ssl, tls, ns):
        self.error('Invalid certificate chain at %s:%s', host, port)
        self._invalid_tls(host, port, ssl, tls, ns)

    def invalid_cert(self, host, port, ssl, tls, ns):
        self.error('Invalid certificate at %s:%s', host, port)
        self._invalid_tls(host, port, ssl, tls, ns)

    def _s2s_stream_feature_cb(self, host, port, features, ssl, tls):
        log.debug('Stream Features: %s:%s: %s', host, port,
                  sorted(features.keys()))
        self._s2s_online.add((host, port))

        features = self._merge_features(features, 's2s')

        self.s2s_starttls_required = features.get(
            'starttls', {}).get('required', False)
        for key in S2S_STREAM_FEATURES:
            setattr(self, 's2s_%s' % key, key in features)
            features.pop(key, None)

        if features:
            log.debug('%s: Unhandled features: %s', self.domain, features)

    def _log(self, message, level, *args):
        try:
            self.logs.create(message=message % args, level=level)
        except Exception as e:
            log.error("Could not format message %s: %s", message, e)

    def warn(self, message, *args):
        self._log(message, logging.WARNING, *args)

    def error(self, message, *args):
        self._log(message, logging.ERROR, *args)

    def verify_ipv6(self, hosts):
        self.ipv6 = True
        try:
            for host in set(hosts):
                if not lookup(host, ipv4=False):
                    self.ipv6 = False
                    if settings.USE_IP6:
                        self.warn('%s has no IPv6 record.', host)
        except:
            self.ipv6 = False

    def verify(self):
        log.debug('Verify %s', self.domain)
        self._c2s_online = set()  # list of online c2s SRV records
        self._s2s_online = set()  # list of online s2s SRV records
        self._c2s_stream_features = None  # private var for stream feature checking
        self._s2s_stream_features = None  # private var for stream feature checking
        self.logs.all().delete()

        # set some defaults:
        self.c2s_ssl_verified = False
        self.c2s_tls_verified = False
        self.s2s_tls_verified = False

        start = datetime.now()
        self._c2s_tls_verified = True
        self._c2s_ssl_verified = True
        self._s2s_tls_verified = True

        # verify c2s-connections
        client_srv = self.verify_srv_client()
        for domain, port, prio in client_srv:
            log.debug('Verify c2s on %s:%s', domain, port)
            # Set to True, the cert_errback will set this to False:
            self.c2s_tls_verified = True

            client = StreamFeatureClient(self,
                callback=self._c2s_stream_feature_cb)
            try:
                with timeout(10, client):
                    client.connect(domain, port, reattempt=False)
                    client.process(block=True)
            except TimeoutException:
                self.error('Could not connect to %s:%s', domain, port)
                self._c2s_tls_verified = False

        # set the last_checked field:
        self.last_checked = datetime.now()
        self.save()

        # return right away if no hosts where seen:
        if self.last_seen is None or self.last_seen < start:
            return

        # verify legacy SSL connections
        if self.ssl_port:
            for host in list(self._c2s_online):
                log.debug('Verify c2s/ssl on %s:%s', host[0], self.ssl_port)
                # Set to True, the cert_errback will set this to False:
                self.c2s_ssl_verified = True

                client = StreamFeatureClient(self,
                    callback=self._c2s_stream_feature_cb)

                try:
                    with timeout(10, client):
                        client.connect(host[0], self.ssl_port,
                                       use_tls=False, use_ssl=True, reattempt=False)
                        client.process(block=True)
                except TimeoutException:
                    self.error('Could not connect to %s:%s', host[0], port)
                    self._c2s_ssl_verified = False

        # verify s2s connections
        server_srv = self.verify_srv_server()
        for domain, port, prio in server_srv:
            log.debug('Verify s2s on %s:%s', domain, port)
            # Set to True, the cert_errback will set this to False:
            self.s2s_tls_verified = True

            client = StreamFeatureClient(self,
                callback=self._s2s_stream_feature_cb, ns='jabber:server')
            try:
                with timeout(10, client):
                    client.connect(domain, port, reattempt=False)
                    client.process(block=True)
            except TimeoutException:
                self.error('Could not connect to %s:%s', domain, port)
                self._s2s_tls_verified = False

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
        else:
            self.c2s_ssl_verified = self._c2s_ssl_verified
            self.c2s_tls_verified = self._c2s_tls_verified
            self.s2s_tls_verified = self._s2s_tls_verified

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
        #TODO: We should somehow decide what 'verified' means.
        return super(Server, self).save(*args, **kwargs)
