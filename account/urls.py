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

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import AuthenticationFormSub
from .forms import SetPasswordForm

app_name = 'account'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('edit/', views.edit, name='edit'),
    path('reset_password/', views.ResetPassword.as_view(), name='reset_password'),
    path('reset_password/done/', views.reset_password_ok, name='reset_password_ok'),
    path('resend_confirmation/', views.resend_confirmation, name='resend_confirmation'),
    path('login/', auth_views.LoginView.as_view(
        authentication_form=AuthenticationFormSub,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view()),
    path('password/', auth_views.PasswordChangeView.as_view(
        #post_change_redirect='/user',  # TODO?
        form_class=SetPasswordForm
    ), name='set_password')
]
