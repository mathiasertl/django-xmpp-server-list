#!/usr/bin/python

import os, sys, datetime
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'xmpplist.settings'
sys.path.append( os.getcwd() )
sys.path.append( os.path.dirname(os.getcwd()) )

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from account.models import UserProfile
from server.models import Server, ServerSoftware, CertificateAuthority, ServerReport, Features

u = User.objects.create(username='mati', email='mati@er.tl', is_superuser=True, is_staff=True)
u.set_password('nopass')
u.save()
p = UserProfile.objects.create(user=u, email_confirmed=True)

startssl = CertificateAuthority.objects.create(name='StartSSL', website='https://www.startssl.com')
cacert = CertificateAuthority.objects.create(name='CAcert', website='https://www.cacert.org')

ejabberd = ServerSoftware.objects.create(name='ejabberd', website='http://www.ejabberd.im',
                                         newest_version='2.1.10')
prosody = ServerSoftware.objects.create(name='prosody', website='http://www.prosody.im',
                                         newest_version='0.8.2')

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