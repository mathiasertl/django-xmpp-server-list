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

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views
from .forms import AuthenticationFormSub
from .forms import SetPasswordForm

# TODO: use path instead of url
# TODO: use namespace instead of account_ prefix in name
urlpatterns = [
    url(r'^$', views.index, name='account'),
    url(r'^create/$', views.create, name='account_create'),
    url(r'^edit/$', views.edit, name='account_edit'),
    url(r'^reset_password/$', views.ResetPassword.as_view(), name='account_reset_password'),
    url(r'^reset_password/done/$', views.reset_password_ok, name='account_reset_password_ok'),
    url(r'^resend_confirmation/$', views.resend_confirmation, name='account_resend_confirmation'),
    url(r'^login/', auth_views.LoginView.as_view(
        template_name='account/login.html',  # TODO: use the default
        authentication_form=AuthenticationFormSub,  # TODO: necessary?
    ), name='login'),
    url(r'^logout/', auth_views.LogoutView.as_view(template_name='logout.html')),  # TODO: use default
    url(r'^password/', auth_views.PasswordChangeView.as_view(
        template_name='account/set_password.html',  # TODO: use default
        #post_change_redirect='/user',  # TODO?
        form_class=SetPasswordForm  # TODO: use default?
    ), name='account_set_password')
]
