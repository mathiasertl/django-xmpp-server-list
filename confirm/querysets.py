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

from django.conf import settings
from django.db.models.query import QuerySet

from datetime import datetime

import hashlib
import time


class ConfirmationKeyQuerySet(QuerySet):
    @property
    def timestamp(self):
        return datetime.now() - settings.CONFIRMATION_TIMEOUT

    @property
    def key(self):
        secret = '%s-%s' % (settings.SECRET_KEY, time.time())
        return hashlib.sha1(secret).hexdigest()

    def create(self, **kwargs):
        if 'key' not in kwargs:
            kwargs['key'] = self.key
        return super(ConfirmationKeyQuerySet, self).create(**kwargs)

    def get_or_create(self, **kwargs):
        defaults = kwargs.get('defaults', {})
        if 'key' not in defaults:
            if 'key' not in kwargs:
                defaults['key'] = self.key
            else:
                defaults['key'] = kwargs['key']

        return super(ConfirmationKeyQuerySet, self).get_or_create(**kwargs)


    def valid(self):
        return self.filter(created__gt=self.timestamp)

    def invalid(self):
        return self.filter(created__lt=self.timestamp)

    def invalidate_outdated(self):
        return self.invalid().delete()

    def invalidate(self, subject):
        return self.filter(subject=subject).delete()
