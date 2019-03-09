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

from celery import shared_task

from django.contrib.auth import get_user_model

from confirm.models import UserConfirmationKey

UserModel = get_user_model()


@shared_task
def send_email_confirmation(user_pk, host, is_secure=True):
    """Send an email to confirm a users email address."""

    user = UserModel.objects.get(pk=user_pk)
    UserConfirmationKey.objects.filter(subject=user, type=UserConfirmationKey.TYPE_EMAIL).delete()
    key = UserConfirmationKey.objects.create(subject=user, type=UserConfirmationKey.TYPE_EMAIL)
    key.send('https' if is_secure else 'http', host)


@shared_task
def send_jid_confirmation(user_pk, host, is_secure=True):
    """Send an XMPP message to confirm a users JID."""

    user = UserModel.objects.get(pk=user_pk)
    UserConfirmationKey.objects.filter(subject=user, type=UserConfirmationKey.TYPE_JID).delete()
    key = UserConfirmationKey.objects.create(subject=user, type=UserConfirmationKey.TYPE_JID)
    key.send('https' if is_secure else 'http', host)
