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
from django.contrib.auth.models import User

from models import UserProfile


class CreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=30,
        help_text='Required, a confirmation email will be sent to this '
        'address.')

    def save(self, commit=True):
        user = super(CreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user

    class Meta:
        model = User
        fields = ('username', 'email',)


class PreferencesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('jid',)


class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=30, required=False)

    def clean(self):
        data = self.cleaned_data

        if data['username']:
            try:
                self.user = User.objects.get(username=data['username'])
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "No user with that username exists.")
        else:
            raise forms.ValidationError(
                "Please give at least one of the fields.")

        return data
