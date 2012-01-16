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
equifax = CertificateAuthority.objects.create(name='Equifax', website='http://www.geotrust.com/resources/root-certificates/',
    certificate=os.path.join(settings.CERTIFICATES_PATH, 'equifax.pem'))
thawte = CertificateAuthority.objects.create(name='Tawte', website='http://www.thawte.com/',
    certificate=os.path.join(settings.CERTIFICATES_PATH, 'thawte.pem'))
rapidssl = CertificateAuthority.objects.create(name='RapidSSL', website='http://www.rapidssl.com/',
    certificate=os.path.join(settings.CERTIFICATES_PATH, 'rapidssl.pem'))
comodo = CertificateAuthority.objects.create(name='Comodo', website='http://www.comodo.com/',
    certificate=os.path.join(settings.CERTIFICATES_PATH, 'comodo.pem'))

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

# common objects:
loc = Point(x=16.37, y=48.20)
today = datetime.date.today()

Server.objects.create(user=u, ca=startssl, software=ejabberd,
    location=loc, launched=today,
    report=ServerReport.objects.create(), features=Features.objects.create(),
    contact='mati@jabber.at', contact_type='J',
    domain='jabber.at', software_version='2.1.10',
)
Server.objects.create(user=u, ca=startssl, software=ejabberd,
    location=loc, launched=today,
    report=ServerReport.objects.create(), features=Features.objects.create(),
    contact='mati@fsinf.at', contact_type='J',
    domain='jabber.fsinf.at', software_version='2.1.10'
)

Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',
    domain='0nl1ne.at', ca=startssl,  software=ejabberd, contact_name='Nikolaus Polak')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='boese-ban.de', ca=startssl,  software=ejabberd,
    contact_name='Tim Schumacher')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='brauchen.info', ca=cacert, software=ejabberd,
    contact_name='Christian Dr?ge')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='climm.org', ca=cacert, software=ejabberd,
    contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='codingteam.net', ca=startssl,
    software=ejabberd, contact_name='Erwan Briand')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='darkdna.net', ca=startssl,
    software=prosody, contact_name='Alex Hanselka')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='deshalbfrei.org', ca=cacert, software=ejabberd, contact_name='Christian Dr?ge')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='draugr.de', ca=cacert, software=ejabberd, contact_name='Christian Dr?ge')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='im.apinc.org', ca=cacert, software=ejabberd, contact_name='Gr?goire Menuel')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='im.flosoft.biz', ca=startssl, software=tigase, contact_name='Florian Jensen')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='internet-exception.de', ca=startssl,
    software=ejabberd, contact_name='Benedikt Marquard')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.ccc.de', ca=cacert, software=ejabberd, contact_name='Peter Schwindt')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.chaotic.de', ca=cacert, software=ejabberd, contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.co.nz', ca=startssl,
    software=ejabberd, contact_name='Paul Willard')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.cz', ca=cacert, software=ejabberd, contact_name='Jan Pinkas')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.fourecks.de', ca=cacert, software=ejabberd, contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.hot-chilli.net', ca=startssl,
    software=ejabberd, contact_name='Martin Sebald')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.iitsp.com', ca=startssl,
    software=openfire, contact_name='Nigel Kukard')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.i-pobox.net', ca=cacert, software=ejabberd, contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.loudas.com', ca=startssl,
    software=ejabberd, contact_name='Paul Willard')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.minus273.org', ca=startssl,
    software=ejabberd, contact_name='Nickola Kolev')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.no', ca=startssl,
    software=ejabberd, contact_name='Stian Barmen')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.rootbash.com', ca=startssl,
    software=openfire, contact_name='Daniel Nauck')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.rueckgr.at', ca=startssl,
    software=ejabberd, contact_name='Paul Staroch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.scha.de', ca=cacert, software=ejabberd, contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.second-home.de', ca=cacert, software=ejabberd, contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.sow.as', ca=cacert, software=ejabberd, contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.tmkis.com', ca=equifax, software=openfire, contact_name='Thomas Kramer')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber.yeahnah.co.nz', ca=startssl,
    software=ejabberd, contact_name='Paul Willard')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabber-br.org', ca=startssl,
    software=ejabberd, contact_name='Thadeu Lima de Souza Cascardo')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10', domain='jabberd.eu', ca=startssl, software=jabberd2,
    contact_name='Benjamin Beskrovny')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10', domain='jabberes.org', ca=startssl,
    software=ejabberd, contact_name='Luis Peralta')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabbim.com', ca=cacert, software=ejabberd, contact_name='Jan Pinkas')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabbim.cz', ca=cacert, software=ejabberd, contact_name='Jan Pinkas')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabbim.pl', ca=cacert, software=ejabberd, contact_name='Jan Pinkas')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabbim.sk', ca=cacert, software=ejabberd, contact_name='Jan Pinkas')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabme.de', ca=cacert, software=ejabberd, contact_name='Christoph Heer')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jabster.pl', ca=startssl,
    software=ejabberd, contact_name='zbyszek@jabster.pl')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='jaim.at', ca=startssl,
    software=ejabberd, contact_name='Friedrich Kron')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='limun.org', ca=cacert, software=ejabberd, contact_name='Mihael Pranji?')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='linuxlovers.at', ca=startssl,
    software=ejabberd, contact_name='Nikolaus Polak')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='macjabber.de', ca=startssl,
    software=ejabberd, contact_name='Jan-Kaspar M?nnich')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='na-di.de', ca=startssl,
    software=openfire, contact_name='Alexander Anger')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='neko.im', ca=startssl,
    software=openfire, contact_name='Nulani t\'Acraya')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='netmindz.net', ca=startssl, software=jabberd2,
    contact_name='Will Tatam')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='njs.netlab.cz', ca=cacert, software=ejabberd,
    contact_name='Jan Pinkas')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='pandion.im', ca=startssl, software=tigase,
    contact_name='Florian Jensen')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='programmer-art.org', ca=startssl,
    software=openfire, contact_name='Daniel G. Taylor')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='richim.org', ca=startssl,
    software=ejabberd, contact_name='Alexandr Shapoval')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='sternenschweif.de', ca=cacert, software=ejabberd,
    contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='swissjabber.ch', ca=startssl,
    software=ejabberd, contact_name='Marco Balmer')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='ubuntu-jabber.de', ca=cacert, software=ejabberd,
    contact_name='Christian Dr?ge')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='thiessen.im', ca=startssl,
    software=prosody, contact_name='Florian Thie?en')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='thiessen.it', ca=startssl,
    software=prosody, contact_name='Florian Thie?en')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='thiessen.org', ca=startssl,
    software=prosody, contact_name='Florian Thie?en')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='ubuntu-jabber.net', ca=cacert, software=ejabberd,
    contact_name='Christian Dr?ge')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='verdammung.org', ca=cacert, software=ejabberd,
    contact_name='Christian Dr?ge')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='xabber.de', ca=cacert, software=ejabberd,
    contact_name='Christian Dr?ge')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='xmpp.jp', ca=startssl,
    software=ejabberd, contact_name='Tsukasa Hamano')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='xmppnet.de', ca=cacert, software=ejabberd,
    contact_name='Michael Grigutsch')
Server.objects.create(user=u, location=loc, contact='fsinf@conference.fsinf.at', contact_type='M',
    report=ServerReport.objects.create(), features=Features.objects.create(), launched=today,
    software_version='2.1.10',domain='zsim.de', ca=cacert, software=openfire,
    contact_name='Kaspar Janssen')