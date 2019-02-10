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

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.template import loader
from django.utils.translation import ugettext_lazy as _

from xmpp.backends import default_xmpp_backend

UserModel = get_user_model()

_fieldattrs = {'class': 'form-control', 'maxlength': 30, }
_emailattrs = _fieldattrs.copy()
_emailattrs['type'] = 'email'
_textwidget = forms.TextInput(attrs=_fieldattrs)
_passwidget = forms.PasswordInput(attrs=_fieldattrs)
_mailwidget = forms.TextInput(attrs=_emailattrs)


class CreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=30, widget=_mailwidget,
        help_text=_(
            'Required, a confirmation email will be sent to this address.')
    )
    username = forms.RegexField(
        label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$', widget=_textwidget,
        help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")
        })
    password1 = forms.CharField(label=_("Password"), widget=_passwidget)
    password2 = forms.CharField(label=_("Confirm"), widget=_passwidget,
                                help_text=_("Enter the same password as above, for verification."))

    def clean_username(self):
        """Override to make the form compatible with custom user models."""

        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            UserModel._default_manager.get(username=username)
        except UserModel.DoesNotExist:
            return username
        raise forms.ValidationError(_('Username already exists.'))

    class Meta:
        model = UserModel
        fields = ('username', 'email', 'jid',)

        widgets = {
            'jid': _textwidget,
        }


class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'email', 'jid')

        widgets = {
            'first_name': _textwidget,
            'last_name': _textwidget,
            'email': _mailwidget,
            'jid': _textwidget,
        }


class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=_passwidget)
    new_password2 = forms.CharField(label=_("Confirm"), widget=_passwidget)


class PasswordResetForm(auth_forms.PasswordResetForm):
    """Override the default form class to also send XMPP messages to JIDs."""

    email = forms.EmailField(label=_("JID or email"), max_length=254)

    def get_users(self, email):
        """Override parent class so we also match the JID of users."""

        active_users = UserModel.objects.jid_or_email(email).filter(is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """Override so we can also send a message via XMPP.

        Note that we do not override the save() method, where we could generate an independent token,
        but this would create a lot of additional code. Here we can just render the same message again.
        """

        super().send_mail(subject_template_name, email_template_name,
                          context, from_email, to_email, html_email_template_name)

        xmpp_template_name = 'account/password_reset_xmpp.txt'
        message = loader.render_to_string(xmpp_template_name, context).strip()
        default_xmpp_backend.send_chat_message(context['user'], message)
