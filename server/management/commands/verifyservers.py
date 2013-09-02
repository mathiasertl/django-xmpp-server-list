import logging
from django.core.management.base import BaseCommand, CommandError
from xmpplist.server.models import Server

class Command(BaseCommand):
    args = '[domain ...]'
    help = 'Verify servers'

    def handle(self, *args, **options):
        if args:
            for domain in args:
                try:
                    Server.objects.get(domain=domain).verify()
                except Server.DoesNotExist:
                    logging.error('Could not find %s', domain)
        else:
            for server in Server.objects.all().order_by('domain'):
                server.verify()
