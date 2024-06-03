import requests
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from entregasapp.models import bdoms, TrackingEventCA
from entregasapp.selializers import TrackingEventCASerializer

class Command(BaseCommand):
    help = 'Populate TrackingEventCA and EventDetail models with data from an external API'

    API_URL = "https://api.correoargentino.com.ar/paqar/v1/tracking"
    HEADERS = {
        "authorization": "Apikey eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxOTEyNSIsIkNMQUlNX1RPS0VOIjoiUEVSTUlTU0lPTl9ERUZBVUxUIiwiaWF0IjoxNjkzMzMzNzM4LCJpc3MiOiJJU1NVRVIifQ.H2G4xWGgpESFMGO06YNYy_0l3tSw3ylmphZW4_y6ifU",
        "agreement": "19125",
    }

    def handle(self, *args, **kwargs):
        # Fetch tracking numbers from bdoms
        tracking_numbers = list(
            bdoms.objects.filter(trackingTransporte__isnull=False)
            .order_by('fechaCreacion')
            .values_list('trackingTransporte', flat=True)
            .distinct()
        )

        if not tracking_numbers:
            self.stdout.write(self.style.WARNING("No tracking numbers found in bdoms."))
            return

        # Determine the starting point based on the last entry date in TrackingEventCA
        last_entry = TrackingEventCA.objects.order_by('-id').first()
        last_date = last_entry.created_at if last_entry else None

        # Process batches
        batch_size = 20
        batch_delay = 2
        error_delay = 4
        retries = 3
        successful_requests = 0
        total_batches = (len(tracking_numbers) + batch_size - 1) // batch_size

        for i in range(total_batches):
            batch = tracking_numbers[i * batch_size:(i + 1) * batch_size]
            if not batch:
                break

            for attempt in range(retries):
                try:
                    response = requests.get(self.API_URL, headers=self.HEADERS, params={
            "extClient": "",
            "trackingNumbers": batch
        })
                    response.raise_for_status()
                    data = response.json()
                    
                    # Process the response data
                    self.process_response_data(data)

                    successful_requests += 1
                    if successful_requests % 500 == 0:
                        self.stdout.write(self.style.SUCCESS("Processed 500 successful requests."))
                    
                    time.sleep(batch_delay)
                    break  # Exit retry loop on success
                except requests.RequestException as e:
                    self.stdout.write(self.style.ERROR(f"Request failed for batch {batch}: {e}"))
                    time.sleep(error_delay)
                    if attempt == retries - 1:
                        self.stdout.write(self.style.ERROR(f"Failed to process batch {batch} after {retries} attempts."))
                        return

    @transaction.atomic
    def process_response_data(self, data):
        for item in data:
            tracking_event_data = {
                'tracking_number': item['trackingNumber'],
                'quantity': item['quantity'],
                'country_id': item['countryId'],
                'service_type': item['serviceType'],
                'events': item['event']
            }

            serializer = TrackingEventCASerializer(data=tracking_event_data)
            if serializer.is_valid():
                serializer.save()
            else:
                self.stdout.write(self.style.ERROR(f"Invalid data for {item['trackingNumber']}: {serializer.errors}"))
        
        # Clear self junk cache to avoid performance issues
        import gc
        gc.collect()