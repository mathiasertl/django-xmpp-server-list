#!/usr/bin/python

import os, sys, datetime
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'xmpplist.settings'
sys.path.append( os.getcwd() )
sys.path.append( os.path.dirname(os.getcwd()) )

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from account.models import UserProfile
from server.models import Server, ServerSoftware, CertificateAuthority, ServerReport, Features

u = User.objects.create(username='mati', email='mati@er.tl', is_superuser=True, is_staff=True)
u.set_password('nopass')
u.save()
p = UserProfile.objects.create(user=u, email_confirmed=True)

other = CertificateAuthority.objects.create(name='other', website='https://www.jabber.at')
startssl = CertificateAuthority.objects.create(name='StartSSL', website='https://www.startssl.com',
    certificate=os.path.join(settings.CERTIFICATES_PATH, 'startssl.pem'))
cacert = CertificateAuthority.objects.create(name='CAcert', website='https://www.cacert.org',
    certificate=os.path.join(settings.CERTIFICATES_PATH, 'cacert.pem'))
gandi = CertificateAuthority.objects.create(name='Gandi', website='http://en.gandi.net/ssl',
    certificate=os.path.join(settings.CERTIFICATES_PATH, 'gandi.pem'))

ejabberd = ServerSoftware.objects.create(name='ejabberd', website='http://www.ejabberd.im',
                                         newest_version='2.1.10')
prosody = ServerSoftware.objects.create(name='Prosody', website='http://www.prosody.im',
                                         newest_version='0.8.2')
tigase = ServerSoftware.objects.create(name='Tigase', website='http://www.tigase.org/',
                                         newest_version='5.1.0')
openfire = ServerSoftware.objects.create(name='Openfire', website='http://www.igniterealtime.org/projects/openfire/',
                                         newest_version='3.7.1')
jabberd14 = ServerSoftware.objects.create(name='jabberd14', website='http://jabberd.org/',
                                         newest_version='1.6.0')
jabberd2 = ServerSoftware.objects.create(name='jabberd2', website='http://codex.xiaoka.com/wiki/jabberd2:start',
                                         newest_version='2.2.14')

Server.objects.create(user=u, ca=startssl, software=ejabberd,
    location=Point(x=16.37, y=48.20),
    report=ServerReport.objects.create(),
    features=Features.objects.create(),
    contact='mati@jabber.at', contact_type='J',
    domain='jabber.at', launched=datetime.date.today(), software_version='2.1.10',
)
Server.objects.create(user=u, ca=startssl, software=ejabberd,
    location=Point(x=16.37, y=48.20),
    report=ServerReport.objects.create(),
    features=Features.objects.create(),
    domain='jabber.fsinf.at',
    contact='mati@fsinf.at', contact_type='J',
    launched=datetime.date.today(), software_version='2.1.10'
)
Server.objects.create(user=u, ca=startssl, software=prosody,
    location=Point(x=16.37, y=48.20),
    report=ServerReport.objects.create(),
    features=Features.objects.create(),
    domain='blah.at',
    contact='mati@fsinf.at', contact_type='J',
    launched=datetime.date.today(), software_version='2.1.10'
)
Server.objects.create(user=u, ca=startssl, software=tigase,
    location=Point(x=16.37, y=48.20),
    report=ServerReport.objects.create(),
    features=Features.objects.create(),
    domain='tigase.im',
    contact='mati@fsinf.at', contact_type='J',
    launched=datetime.date.today(), software_version='2.1.10'
)
Server.objects.create(user=u, ca=startssl, software=openfire,
    location=Point(x=16.37, y=48.20),
    report=ServerReport.objects.create(),
    features=Features.objects.create(),
    domain='orcalab.net',
    contact='mati@fsinf.at', contact_type='J',
    launched=datetime.date.today(), software_version='2.1.10'
)