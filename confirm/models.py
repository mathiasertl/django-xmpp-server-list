import time

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

from xmpplist.server.models import Server

CONFIRMATION_TYPE_CHOICES=(
    ('J', 'JID'),
    ('E', 'e-mail'),
)

class ConfirmationKey(models.Model):
    key = models.CharField(max_length=128, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=CONFIRMATION_TYPE_CHOICES)
    
    def __init__(self, *args, **kwargs):
        super(ConfirmationKey, self).__init__(*args, **kwargs)
        self.key = self.set_random_key()
        
    def send_mail(self, to, subject, message):
        frm = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, frm, [to], fail_silently=True)
        
    def send_jid(self, to, subject, message):
        print('XMPP message: To: %s\nSubject: %s\nMessage: %s' % (to, subject, message))
    
    class Meta:
        abstract = True
        
class UserConfirmationKey(ConfirmationKey):
    user = models.ForeignKey(User, related_name='confirmations')        
    
    def send(self, request):
        message = render_to_string("confirm/user_contact.txt", {'request': request, 'key': self})
        subject = 'Confirm your email address'
        
        if self.type == 'E':    
            self.send_mail(self.user.email, subject, message)
        else:
            self.send_jid(self.user.profile.jid, subject, message)
    
    def set_random_key(self):
        salt = sha_constructor('%s-%s-%s' % (settings.SECRET_KEY, time.time(), self.type)).hexdigest()
        return sha_constructor('%s-%s-%s' % (salt, self.user.username, self.user.email)).hexdigest()
        
class UserPasswordResetKey(UserConfirmationKey):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetKey, self).__init__(*args, **kwargs)
        if 'type' not in kwargs:
            if self.user.profile.email_confirmed:
                self.type = 'M'
            else:
                self.type = 'J'
            
    def send(self, request):
        message = render_to_string("confirm/user_password_reset.txt",
            {'request': request, 'key': self}
        )
        subject = 'Confirm your email address'
        
        if self.type == 'E':
            # send confirmation
            self.send_mail(self.user.email, subject, message)
        else:
            print('confirm jid...')
    
class ServerConfirmationKey(ConfirmationKey):
    server = models.ForeignKey(Server, related_name='confirmations')
    
    def __init__(self, *args, **kwargs):
        super(ServerConfirmationKey, self).__init__(*args, **kwargs)
        self.type = self.server.contact_type
    
    def send(self, request):
        message = render_to_string("confirm/server_contact.txt", {'request': request, 'key': self})
        subject = 'Confirm your email address'
        
        if self.type == 'E':    
            self.send_mail(self.server.contact, subject, message)
        else:
            self.send_jid(self.server.contact, subject, message)
    
    def set_random_key(self):
        salt = sha_constructor('%s-%s' % (settings.SECRET_KEY, time.time())).hexdigest()
        return sha_constructor('%s-%s' % (salt, self.server.domain)).hexdigest()