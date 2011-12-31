import time

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.hashcompat import sha_constructor
from django.template.loader import render_to_string
from django.core.mail import send_mail

def get_random_key(user):
    salt = sha_constructor('%s-%s' % (settings.SECRET_KEY, time.time()))
    salt = salt.hexdigest()
    return sha_constructor('%s-%s-%s' % (salt, user.username, user.email)).hexdigest()

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    email_confirmed = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.user.username

class ConfirmationKey(models.Model):
    key = models.CharField(max_length=128, unique=True)
    sent = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='confirmations')
        
    def send(self, request):
        # send confirmation
        message = render_to_string("users/email.txt", {
            'request': request, 'user': self.user, 'key': self.key
        })
        subject = 'Confirm your email address'
        frm = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, frm, [self.user.email], fail_silently=True)
    
    def __unicode__(self):
        return self.user.username
    