from django.core.management.base import BaseCommand
from entregasapp.models import bdoms, TrackingEventCA, OrderTracking
from django.db import transaction, connections
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate OrderTracking model with data from bdoms and TrackingEventCA'

    BATCH_SIZE = 10000

    def handle(self, *args, **kwargs):
        tracking_events = TrackingEventCA.objects.all()
        batch = []
        conflicts = []

        for tracking_event in tracking_events.iterator():
            try:
                order_numbers = bdoms.objects.filter(trackingTransporte=tracking_event.tracking_number).values_list('pedido', flat=True).distinct()
                for order_number in order_numbers:
                    batch.append(OrderTracking(pedido=order_number, tracking_event=tracking_event))
                    if len(batch) >= self.BATCH_SIZE:
                        self.save_batch(batch, conflicts)
                        batch = []
                self.stdout.write(self.style.SUCCESS(f"Successfully processed tracking event: {tracking_event.tracking_number}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing tracking event {tracking_event.tracking_number}: {str(e)}"))

        if batch:
            self.save_batch(batch, conflicts)

        if conflicts:
            self.stdout.write(self.style.WARNING(f"Conflicts encountered: {conflicts}"))

        self.stdout.write(self.style.SUCCESS("Completed populating OrderTracking model."))

    def save_batch(self, batch, conflicts):
        try:
            with transaction.atomic():
                OrderTracking.objects.bulk_create(batch, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Successfully saved batch of {len(batch)} records."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving batch: {str(e)}"))
            conflicts.extend(batch)