from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from models import UserProfile

class CreationForm(UserCreationForm):
    email = forms.EmailField(max_length=30,
        help_text='Required, a confirmation email will be sent to this address.')
    
    def save(self, commit=True):
        user = super(CreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
            # create default profile:
            UserProfile.objects.create(user=user)
            
        return user
    
    class Meta:
        model = User
        fields = ('username', 'email', )
        
class PreferencesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class PasswordForm(forms.Form):
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)
    password_confirm = forms.CharField(min_length=8, widget=forms.PasswordInput)
    
    def clean(self):
        data = self.cleaned_data
        if 'password' in data and 'password_confirm' in data and data['password'] != data['password_confirm']:
            raise forms.ValidationError("The two passwords didn't match!")
            
        return self.cleaned_data
    
class PasswordResetForm(forms.Form):
    username = forms.CharField()