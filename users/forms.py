from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from models import UserProfile

class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=30,
        help_text='Required, a confirmation email will be sent to this address.')
    
    def save(self, commit=True):
        user = super(MyUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
            # create default profile:
            UserProfile.objects.create(user=user)
            
        return user
    
    class Meta:
        model = User
        fields = ('username', 'email', )