import time

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    email_confirmed = models.BooleanField(default=False)
    
    jid = models.CharField(max_length=128,
        help_text="Required, a confirmation message will be sent to this address.")
    jid_confirmed =  models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.user.username
    