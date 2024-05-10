from django.core.management.base import BaseCommand
from entregasapp.models import bdoms

class Command(BaseCommand):
    help = 'Delete all data from bdoms table'

    def handle(self, *args, **kwargs):
        # Delete all data from the bdoms table
        bdoms.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('All data deleted successfully.'))