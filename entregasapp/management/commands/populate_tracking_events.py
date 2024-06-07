import requests
import time
import json
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from entregasapp.models import bdoms, TrackingEventCA, EventDetail
from entregasapp.selializers import TrackingEventCASerializer, EventDetailSerializer

class Command(BaseCommand):
    help = 'Populate TrackingEventCA and EventDetail models with data from an external API'

    API_URL = "https://api.correoargentino.com.ar/paqar/v1/tracking"
    # API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxOTEyNSIsIkNMQUlNX1RPS0VOIjoiUEVSTUlTU0lOX0RFRkFVTFQiLCJpYXQiOjE2OTMzMzM3MzgsImlzcyI6IklTU1VFSVIifQ.H2G4xWGgpESFMGO06YNYy_0l3tSw3ylmphZW4_y6ifU"
    # AGREEMENT = "19125"
    HEADERS = {
        "authorization": "Apikey eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxOTEyNSIsIkNMQUlNX1RPS0VOIjoiUEVSTUlTU0lPTl9ERUZBVUxUIiwiaWF0IjoxNjkzMzMzNzM4LCJpc3MiOiJJU1NVRVIifQ.H2G4xWGgpESFMGO06YNYy_0l3tSw3ylmphZW4_y6ifU",
        "agreement": "19125",
    }
    VALID_TRACKING_REGEX = re.compile(r'^19.{16}$')  # Adjust the length as needed

    def handle(self, *args, **kwargs):
        # Fetch tracking numbers from bdoms and filter with regex
        tracking_numbers = list(
            bdoms.objects.filter(trackingTransporte__isnull=False)
            .order_by('fechaCreacion')
            .values_list('trackingTransporte', flat=True)
            .distinct()
        )
        
        # Filter tracking numbers with regex
        valid_tracking_numbers = [tn for tn in tracking_numbers if self.VALID_TRACKING_REGEX.match(tn)]

        if not valid_tracking_numbers:
            self.stdout.write(self.style.WARNING("No valid tracking numbers found in bdoms."))
            return

        # Process batches
        batch_size = 20
        batch_delay = 1
        error_delay = 4
        retries = 3
        successful_requests = 0
        cached_data = []
        total_batches = (len(valid_tracking_numbers) + batch_size - 1) // batch_size
        atomizer_trigger = 1

        for i in range(total_batches):
            batch = valid_tracking_numbers[i * batch_size:(i + 1) * batch_size]
            if not batch:
                break

            for attempt in range(retries):
                try:
                    parameters = {
                        "extClient": "",
                        "trackingNumbers": batch
                    }
                    print(f"Requesting batch: {parameters}")  # Debugging line
                    response = requests.get(self.API_URL, headers=self.HEADERS, params=parameters)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Cache the response data
                    cached_data.extend(data)
                    successful_requests += 1
                    print(f"batch {successful_requests} ok")
                    
                    if successful_requests % atomizer_trigger == 0:
                        self.stdout.write(self.style.SUCCESS("Processed 500 successful requests."))
                        self.save_cached_data(cached_data)
                        cached_data = []  # Clear cache after saving
                    
                    time.sleep(batch_delay)
                    break  # Exit retry loop on success
                except requests.RequestException as e:
                    self.stdout.write(self.style.ERROR(f"Request failed for batch {batch}: {e}"))
                    time.sleep(error_delay)
                    if attempt == retries - 1:
                        self.stdout.write(self.style.ERROR(f"Failed to process batch {batch} after {retries} attempts."))
                        return

        # Save any remaining cached data
        if cached_data:
            self.save_cached_data(cached_data)

    @transaction.atomic
    def save_cached_data(self, cached_data):
        for item in cached_data:
            print(item)
            country_id = item.get('countryId')
            service_type = item.get('serviceType')

            # Check for None, null, or empty values and set default values
            if not country_id:
                country_id = 'AR'
            if not service_type:
                service_type = 'SD'

            tracking_event_data = {
                'tracking_number': item.get('trackingNumber'),
                'quantity': item.get('quantity'),
                'country_id': country_id,
                'service_type': service_type,
                'events': item.get('event', [])
            }
            print(tracking_event_data)

            serializer = TrackingEventCASerializer(data=tracking_event_data)
            if serializer.is_valid():
                tracking_event = serializer.save()
                # Process and save EventDetail
                events_data = tracking_event_data['events']
                for event_data in events_data:
                    event_data['tracking_event'] = tracking_event.id
                    event_serializer = EventDetailSerializer(data=event_data)
                    if event_serializer.is_valid():
                        event_serializer.save()
                    else:
                        self.stdout.write(self.style.ERROR(f"Invalid event data for {item.get('trackingNumber')}: {event_serializer.errors}"))
            else:
                self.stdout.write(self.style.ERROR(f"Invalid data for {item.get('trackingNumber')}: {serializer.errors}"))
        
        # Clear self junk cache to avoid performance issues
        import gc
        gc.collect()