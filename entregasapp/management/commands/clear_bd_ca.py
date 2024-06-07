from django.core.management.base import BaseCommand
from entregasapp.models import TrackingEventCA

class Command(BaseCommand):
    help = 'Delete all data from TrackingEventCA table'

    def handle(self, *args, **kwargs):
        
        TrackingEventCA.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('All data deleted successfully.'))