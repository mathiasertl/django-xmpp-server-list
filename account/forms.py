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

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class CreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=30,
        help_text='Required, a confirmation email will be sent to this '
        'address.')

    def clean_username(self):
        """Override to make the form compatible with custom user models."""

        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            UserModel._default_manager.get(username=username)
        except UserModel.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


    class Meta:
        model = UserModel
        fields = ('username', 'email', 'jid',)


class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'email', 'jid')


class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=30, required=False)

    def clean(self):
        data = self.cleaned_data

        if data['username']:
            try:
                self.user = UserModel.objects.get(username=data['username'])
            except UserModel.DoesNotExist:
                raise forms.ValidationError(
                    "No user with that username exists.")
        else:
            raise forms.ValidationError(
                "Please give at least one of the fields.")

        return data
