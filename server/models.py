# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list).
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify
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
# along with django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.

import copy
import logging
import os
import signal
from contextlib import contextmanager
from datetime import datetime

import geoip2.database
import geoip2.errors
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _

from core.models import BaseModel
from core.utils import int_to_hex
from server.constants import C2S_STREAM_FEATURES
from server.constants import CONTACT_TYPE_EMAIL
from server.constants import CONTACT_TYPE_JID
from server.constants import CONTACT_TYPE_MUC
from server.constants import CONTACT_TYPE_WEBSITE
from server.constants import S2S_STREAM_FEATURES
from server.dns import lookup
from server.dns import srv_lookup
from server.querysets import ServerQuerySet
from server.util import get_siteinfo
from xmpp.clients import StreamFeatureClient

log = logging.getLogger(__name__)


class TimeoutException(Exception):
    pass


def launch_year_validator(value):
    if value < 2001:
        raise ValidationError(_('Launch year may not be prior to 2001.'))
    if value > timezone.now().year:
        raise ValidationError(_('Launch year may not be in the future.'))


def launch_year_default():
    return timezone.now().year


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
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=30, null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _('Certificate authorities')

    def __str__(self):
        return self.name

    def get_display_name(self):
        return self.display_name or self.name


class Certificate(BaseModel):
    ca = models.ForeignKey(CertificateAuthority, on_delete=models.PROTECT, related_name='certificates')
    server = models.ForeignKey('server.Server', on_delete=models.CASCADE, related_name='certificates')

    # NOTE: Highly unlikely, it's possible for 2 certs to have the same serial (e.g. from different CAs)
    serial = models.CharField(max_length=64, help_text=_('The serial of the certificate.'))
    pem = models.TextField(unique=True, help_text=_('The full certificate as PEM.'))

    valid_from = models.DateTimeField(help_text=_('When this certificate was issued.'))
    valid_until = models.DateTimeField(help_text=_('When this certificate expires.'))

    first_seen = models.DateTimeField(help_text=_('When we first saw this certificate'))
    last_seen = models.DateTimeField(help_text=_('When we last saw this certificate'))

    def __str__(self):
        return self.serial

    @property
    def valid(self):
        now = timezone.now()
        return self.valid_from <= now and self.valid_until >= now


class ServerSoftware(models.Model):
    name = models.CharField(max_length=16)
    website = models.URLField()
    newest_version = models.CharField(max_length=8)

    class Meta:
        verbose_name_plural = _('Server software')

    def __str__(self):
        return self.name


class Features(models.Model):
    # features:
    has_muc = models.BooleanField(default=False)
    has_irc = models.BooleanField(default=False)
    has_vcard = models.BooleanField(default=False)
    has_pep = models.BooleanField(default=False)
    has_proxy = models.BooleanField(default=False)
    has_webpresence = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = _('Features')

    def __str__(self):
        try:
            domain = self.server.domain
        except Exception:
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
    server = models.ForeignKey('Server', on_delete=models.CASCADE, related_name='logs')
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
    CONTACT_TYPE_EMAIL = CONTACT_TYPE_EMAIL
    CONTACT_TYPE_JID = CONTACT_TYPE_JID
    CONTACT_TYPE_MUC = CONTACT_TYPE_MUC
    CONTACT_TYPE_WEBSITE = CONTACT_TYPE_WEBSITE
    CONTACT_TYPE_CHOICES = (
        (CONTACT_TYPE_MUC, 'MUC'),
        (CONTACT_TYPE_JID, 'JID'),
        (CONTACT_TYPE_EMAIL, 'e-mail'),
        (CONTACT_TYPE_WEBSITE, 'website'),
    )
    #####################
    # Basic information #
    #####################
    domain = models.CharField(unique=True, max_length=60,
                              help_text="The primary domain of your server.")
    launched = models.PositiveSmallIntegerField(
        validators=[launch_year_validator], default=launch_year_default,
        help_text='Year this server was launched.')
    website = models.URLField(blank=True, help_text=_(
        "Homepage with information about your server. If left empty, the default is https://<domain>."))
    policy_url = models.URLField(
        blank=True, verbose_name=_('Policy URL'),
        help_text=_('A URL describing any terms and conditions for using your server.')
    )
    registration_url = models.URLField(
        blank=True, verbose_name=_('Registration URL'),
        help_text=_('A URL where users can create an account on your server.')
    )

    ###########
    # Contact #
    ###########
    contact = models.CharField(
        max_length=60, help_text="The address where the server-admins can be reached.")
    contact_type = models.CharField(
        max_length=1, choices=CONTACT_TYPE_CHOICES, default='J',
        help_text="What type your contact details are. This setting will affect how the contact details are "
        "rendered on the front page. If you choose a JID or an e-mail address, you will receive an "
        "automated confirmation message.")
    contact_name = models.CharField(
        max_length=60, blank=True,
        help_text="If you want to display a custom link-text for your contact details, give it here.")
    contact_verified = models.BooleanField(default=False, help_text=_('If contact information is verified.'))

    ###############
    # Maintenance #
    ###############
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='servers')
    added = models.DateField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True)  # last seen online
    last_checked = models.DateTimeField(null=True, blank=True)  # last check completed (None == never checked)

    # geolocation:
    country = models.CharField(default='', null=True, blank=True, max_length=100,
                               help_text="Country the server is located in.")

    # information about the service:
    cert = models.ForeignKey(
        Certificate, on_delete=models.PROTECT, null=True, verbose_name=_('Current certificate'),
        related_name='+',  # no backwards relation
        help_text=_('The current certificate used by this server.')
    )
    ca = models.ForeignKey(
        CertificateAuthority, on_delete=models.PROTECT,
        related_name='servers', verbose_name='CA', blank=True, null=True,
        help_text="The Certificate Authority of the certificate used in SSL/TLS connections.")

    # moderation:
    moderated = models.NullBooleanField(default=None)
    moderators_notified = models.BooleanField(default=False)
    moderation_message = models.TextField(default='')
    features = models.OneToOneField(Features, on_delete=models.CASCADE, related_name='server')

    # queried information
    software = models.ForeignKey(ServerSoftware, on_delete=models.CASCADE, related_name='servers',
                                 null=True, blank=True)
    software_version = models.CharField(max_length=30, blank=True)

    # DNS-related information:
    c2s_srv_records = models.BooleanField(default=False)
    s2s_srv_records = models.BooleanField(default=False)
    ipv6 = models.BooleanField(default=False)

    # SSL/TLS verification
    c2s_tls_verified = models.BooleanField(default=False)
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

    objects = ServerQuerySet.as_manager()

    class Meta:
        permissions = (
            ('moderate', 'can moderate servers'),
        )

    def __str__(self):
        return self.domain

    def get_absolute_url(self):
        return reverse('server:status', kwargs={'pk': self.pk})

    def _c2s_stream_feature_cb(self, host, port, features, ssl, tls):
        self.info("Verified connectivity for %s" % (self.pprint_host(host, port)))

        log.debug('Stream Features: %s:%s: %s', host, port, sorted(features.keys()))
        self._c2s_online.add((host, port))
        self.last_seen = datetime.now()  # we saw an online host

        features = self._merge_features(features, 'c2s', ssl)

        self.c2s_starttls_required = features.get('starttls', {}).get('required', False)
        for key in C2S_STREAM_FEATURES:
            setattr(self, 'c2s_%s' % key, key in features)
            features.pop(key, None)

        if features:
            log.debug('%s: Unhandled features: %s', self.domain, features)

    def _invalid_tls(self, host, port, ns):
        if ns == 'jabber:client':  # c2s connection
            self._c2s_tls_verified = False
        elif ns == 'jabber:server':  # s2s connection
            self._s2s_tls_verified = False
        else:
            log.error('Unknown namespace: %s', ns)

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

    def autoconfirmed(self, typ, address):
        if typ == 'E' and self.user.email == address and self.user.email_confirmed:
            return True
        elif typ == 'J' and self.user.jid == address and self.user.jid_confirmed:
            return True

    def automatic_verification(self):
        if self.contact_type in ['J', 'E'] and not self.contact_verified:
            return True
        return False

    @property
    def contact_ok(self):
        """True if the contact information for this server is ok

        This is true if the servers contact is verified *and* the user has verified contact information.
        """
        return self.contact_verified and self.user.email_confirmed and self.user.jid_confirmed

    def do_contact_verification(self, request):
        typ = self.contact_type

        # Set contact_verified if it sthe same as your email or JID:
        if self.autoconfirmed(typ, self.contact):
            self.contact_verified = True
        elif typ in ['J', 'E']:
            key = self.confirmations.create(subject=self, type=self.contact_type)
            protocol, domain = get_siteinfo(request)
            key.send(protocol, domain)

    def get_contact_text(self):
        if self.contact_name:
            return self.contact_name
        return self.contact

    def get_website(self):
        if self.website:
            return self.website
        else:
            return 'https://%s' % self.domain

    def handle_cert(self, pem):
        self.ca = CertificateAuthority.objects.get_or_create(name='foo')[0]

        now = timezone.now()
        x509_cert = x509.load_pem_x509_certificate(pem.encode('utf-8'), default_backend())
        try:
            cert, created = Certificate.objects.get_or_create(pem=pem, defaults={
                'ca': self.ca,  # TODO
                'first_seen': now,
                'last_seen': now,
                'serial': int_to_hex(x509_cert.serial_number),
                'server': self,
                'valid_from': x509_cert.not_valid_before,
                'valid_until': x509_cert.not_valid_after,
            })
        except Exception as e:
            log.exception(e)

        if not created:  # update information
            cert.last_seen = now
            cert.save()

    def invalid_cert(self, host, port, ssl, tls, ns):
        self.error('Invalid certificate at %s', self.pprint_host(host, port))
        self._invalid_tls(host, port, ns)

    def invalid_chain(self, host, port, ns):
        self.error('Invalid certificate chain at %s', self.pprint_host(host, port))
        self._invalid_tls(host, port, ns)

    @property
    def location(self):
        return self.country or _('Unknown')

    def pprint_host(self, host, port):
        host = '[%s]' % host if ':' in host else host
        return '%s:%s' % (host, port)

    def set_location(self, hostname):
        ip = hostname[0]

        if not os.path.exists(settings.GEOIP_COUNTRY_DB):
            log.error('%s: File not found, refresh GeoIP databases!')
            return

        try:
            reader = geoip2.database.Reader(settings.GEOIP_COUNTRY_DB)
            self.country = reader.country(ip).country.name
        except geoip2.errors.GeoIP2Error as e:
            log.exception(e)

    @property
    def verified(self):
        if self.last_seen is None:
            return None
        return self.c2s_srv_records and self.s2s_srv_records and self.c2s_tls_verified \
            and self.s2s_tls_verified and self.c2s_starttls

    @verified.setter
    def verified(self, value):
        if not value:
            self.c2s_srv_records = False
            self.s2s_srv_records = False
            self.c2s_tls_verified = False
            self.s2s_tls_verified = False
            self.c2s_starttls = False

    def verify(self):
        log.debug('Verify %s', self.domain)
        self._c2s_online = set()  # list of online c2s SRV records
        self._s2s_online = set()  # list of online s2s SRV records
        self._c2s_stream_features = None  # private var for stream feature checking
        self._s2s_stream_features = None  # private var for stream feature checking
        self.logs.all().delete()

        # set some defaults:
        self.c2s_tls_verified = False
        self.s2s_tls_verified = False

        start = datetime.now()
        self._c2s_tls_verified = True
        self._s2s_tls_verified = True

        get_ca = True

        # verify c2s-connections
        client_srv = self.verify_srv_client()
        for domain, port, prio in client_srv:
            log.debug('Verify c2s on %s:%s', domain, port)
            # Set to True, the cert_errback will set this to False:
            self.c2s_tls_verified = True

            client = StreamFeatureClient(self, callback=self._c2s_stream_feature_cb, get_ca=get_ca)
            get_ca = False
            try:
                with timeout(10, client):
                    client.connect(domain, port, reattempt=False)
                    client.process(block=True)
            except TimeoutException:
                self.error('Could not connect to %s:%s', domain, port)
                self._c2s_tls_verified = False

        # set the last_checked field:
        self.last_checked = datetime.now()

        # return right away if no hosts where seen:
        if self.last_seen is None or self.last_seen < start:
            self.save()
            return

        # verify s2s connections
        server_srv = self.verify_srv_server()
        for domain, port, prio in server_srv:
            log.debug('Verify s2s on %s:%s', domain, port)
            # Set to True, the cert_errback will set this to False:
            self.s2s_tls_verified = True

            client = StreamFeatureClient(self, callback=self._s2s_stream_feature_cb,
                                         ns='jabber:server')
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
            self.country = ''

        # check IPv6 DNS records:
        self.verify_ipv6([r[0] for r in client_srv + server_srv])

        # If my CA has no certificates (the "other" ca), no certificates were
        # actually verified, so set them to false manually.
        if self.ca is None:
            print('self.ca is None!')
            self.c2s_tls_verified = False
            self.s2s_tls_verified = False
        else:
            self.c2s_tls_verified = self._c2s_tls_verified
            self.s2s_tls_verified = self._s2s_tls_verified

        self.save()

        if self.verified:
            log.info('... verified %s', self.domain)
        else:
            log.info('... failed to verify %s', self.domain)

    def verify_ipv6(self, hosts):
        self.ipv6 = True
        try:
            for host in set(hosts):
                if not lookup(host, ipv4=False):
                    self.ipv6 = False
                    if settings.USE_IP6:
                        self.warn('%s has no IPv6 record.', host)
        except Exception:
            self.ipv6 = False

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
            log.info('Server has no c2s SRV records.')
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
            log.info('Server has no s2s SRV records.')

        return hosts

    def _s2s_stream_feature_cb(self, host, port, features, ssl, tls):
        log.debug('Stream Features: %s: %s', self.pprint_host(host, port), sorted(features.keys()))
        self._s2s_online.add((host, port))

        features = self._merge_features(features, 's2s')

        self.s2s_starttls_required = features.get('starttls', {}).get('required', False)
        for key in S2S_STREAM_FEATURES:
            setattr(self, 's2s_%s' % key, key in features)
            features.pop(key, None)

        if features:
            log.debug('%s: Unhandled features: %s', self.domain, features)

    ###########
    # Logging #
    ###########
    def _log(self, message, level, *args):
        try:
            self.logs.create(message=message % args, level=level)
        except Exception as e:
            log.error("Could not format message %s: %s", message, e)

    def error(self, message, *args):
        self._log(message, logging.ERROR, *args)

    def info(self, message, *args):
        self._log(message, logging.INFO, *args)

    def warn(self, message, *args):
        self._log(message, logging.WARNING, *args)
