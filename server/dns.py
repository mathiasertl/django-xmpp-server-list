# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-list (https://list.jabber.at).
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

from __future__ import unicode_literals, absolute_import

import dns.resolver

from django.conf import settings


def srv_lookup(domain, service, proto='tcp'):
    """
    Function for doing SRV-lookups. Returns a list of host/port tuples for
    the given srv-record.
    """
    record = '_%s._%s.%s' % (service, proto, domain)
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

    # return sorted by priority
    return sorted(hosts, key=lambda host: host[2])


def lookup(host, ipv4=True, ipv6=True):
    assert ipv4 or ipv6, "Either ipv4 or IPv6 must be True"
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 3.0

    hosts = []

    if ipv4 and settings.USE_IP4:
        try:
            hosts += [a.address for a in resolver.query(host, 'A')]
        except:
            pass

    if ipv6 and settings.USE_IP6:
        try:
            hosts += [a.address for a in resolver.query(host, 'AAAA')]
        except:
            pass
    return hosts
