#!/usr/bin/python

import os, sys, datetime
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'xmpplist.settings'
sys.path.append( os.getcwd() )
sys.path.append( os.path.dirname(os.getcwd()) )

from django.contrib.auth.models import User
from account.models import UserProfile
from server.models import Server, ServerSoftware, CertificateAuthority

for server in Server.objects.filter(verified=None):
    print(server.verify())