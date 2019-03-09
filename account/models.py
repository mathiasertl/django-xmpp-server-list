# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list)
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

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from .querysets import UserQuerySet


class LocalUser(AbstractUser):
    objects = BaseUserManager.from_queryset(UserQuerySet)()

    email = models.EmailField(
        _('email address'), unique=True,
        help_text=_('Required, a confirmation message will be sent to this address.'))
    jid = models.CharField(
        _('JID'), max_length=128, unique=True,
        help_text=_('Required, a confirmation message will be sent to this address.'))

    email_confirmed = models.BooleanField(default=False)
    jid_confirmed = models.BooleanField(default=False)
