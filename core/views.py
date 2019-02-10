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

from django.shortcuts import redirect


class AnonymousRequiredMixin:
    """Mixin to redirect authenticated users to a different page.

    Set the ``authenticated_url`` property of a view using this mixin to redirect authenticated users to
    that url.
    """
    def get_authenticated_url(self):
        return self.authenticated_url

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_authenticated_url())

        return super().dispatch(request, *args, **kwargs)
