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

from django import template
from django.forms.fields import DateField
from django.utils import six

register = template.Library()


@register.filter
def fieldvalue(field):
    if hasattr(field.field, 'choices'):
        for k, v in field.field.choices:
            if k == field.value():
                return v
        return 'key not found'
    elif isinstance(field.field, DateField):
        val = field.value()
        if isinstance(val, six.string_types):
            return val
        elif val is None:
            return ''
        return field.value().strftime('%Y-%m-%d')
    else:
        return field.value()
