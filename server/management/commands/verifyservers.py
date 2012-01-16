from django.core.management.base import BaseCommand, CommandError
from xmpplist.server.models import Server

class Command(BaseCommand):
#    args = '<poll_id poll_id ...>'
    help = 'Verify servers'

    def handle(self, *args, **options):
        for server in Server.objects.all().order_by('domain'):
            server.verify()