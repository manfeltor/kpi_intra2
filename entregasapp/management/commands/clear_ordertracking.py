from django.core.management.base import BaseCommand
from entregasapp.models import OrderTracking

class Command(BaseCommand):
    help = 'Delete all data from OrderTracking table'

    def handle(self, *args, **kwargs):
        
        OrderTracking.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'All data from {OrderTracking} deleted successfully.'))