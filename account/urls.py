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

from django.conf.urls import patterns
from django.conf.urls import url

from forms import AuthenticationFormSub
from forms import SetPasswordForm
from views import ResetPassword

urlpatterns = patterns(
    'account.views',
    url(r'^$', 'index', name='account'),
    url(r'^create/$', 'create', name='account_create'),
    url(r'^edit/$', 'edit', name='account_edit'),
    url(r'^reset_password/$', ResetPassword.as_view(),
        name='account_reset_password'),
    url(r'^reset_password/done/$', 'reset_password_ok',
        name='account_reset_password_ok'),
    url(r'^resend_confirmation/$', 'resend_confirmation',
        name='account_resend_confirmation'),
)
urlpatterns += patterns(
    '',
    url(r'^login/', 'django.contrib.auth.views.login',
        {'template_name': 'account/login.html',
         'authentication_form': AuthenticationFormSub,
        }, name='login'),
    url(r'^logout/', 'django.contrib.auth.views.logout',
        {'template_name': 'logout.html'}),
    url(r'^password/', 'django.contrib.auth.views.password_change',
        {'template_name': 'account/set_password.html',
         'post_change_redirect': '/user',
         'password_change_form': SetPasswordForm,
         },
        name='account_set_password'
        )
)
