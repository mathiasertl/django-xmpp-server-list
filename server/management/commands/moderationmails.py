from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template import Context
from django.template import loader

from xmpplist.server.models import Server
from xmpplist.server.util import get_siteinfo


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        perm = Permission.objects.get(codename='moderate')
        query = Q(groups__permissions=perm) | Q(user_permissions=perm)
        users = User.objects.filter(query | Q(is_superuser=True)).distinct()
        protocol, domain = get_siteinfo()

        servers = Server.objects.filter(moderated=None)
        if not servers:
            return

        subject = '[%s] %s servers awaiting moderation' % (
            settings.SITENAME, len(servers)
        )

        t = loader.get_template('mail/moderationmail.html')
        for user in users:
            c = Context({
                'servers': servers,
                'user': user,
                'sitename': settings.SITENAME,
                'protocol': protocol,
                'domain': domain,
            })

            body = t.render(c)

            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                          [user.email], fail_silently=False)
