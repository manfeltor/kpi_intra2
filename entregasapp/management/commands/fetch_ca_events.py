from django.core.management.base import BaseCommand
from django.db import transaction
from entregasapp.models import bdoms
import requests
import time
from entregasapp.models import TrackingEventCA

class Command(BaseCommand):
    help = 'Fetch and store tracking data for bdoms'

    def handle(self, *args, **options):
        api_key = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxOTEyNSIsIkNMQUlNX1RPS0VOIjoiUEVSTUlTU0lPTl9ERUZBVUxUIiwiaWF0IjoxNjkzMzMzNzM4LCJpc3MiOiJJU1NVRVIifQ.H2G4xWGgpESFMGO06YNYy_0l3tSw3ylmphZW4_y6ifU"
        agreement = "19125"
        url = "https://api.correoargentino.com.ar/paqar/v1/tracking"
        with transaction.atomic():
            # Filter bdoms entries with non-null, valid-length tracking numbers
            tracking_numbers = bdoms.objects.exclude(trackingTransporte__isnull=True).exclude(trackingTransporte__exact='').filter(trackingTransporte__length=18).values_list('trackingTransporte', flat=True).distinct()
            tracking_numbers = list(tracking_numbers)

            # Process in chunks of 20
            for i in range(0, len(tracking_numbers), 20):
                chunk = tracking_numbers[i:i+20]
                params = {
                    "extClient": "",
                    "trackingNumbers": chunk
                }
                headers = {
                    "Authorization": f"Apikey {api_key}",
                    "agreement": agreement
                }
                try:
                    response = requests.get(url, headers=headers, params=params)
                    if response.status_code == 200:
                        for tracking_number, info in zip(chunk, response.json()):
                            TrackingEventCA.objects.update_or_create(
                                tracking_number=tracking_number,
                                defaults={'data': info}
                            )
                        self.stdout.write(self.style.SUCCESS(f'Successfully processed chunk starting at index {i}'))
                    else:
                        raise Exception(f"API request failed for chunk starting at index {i}: {response.status_code} - {response.text}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing chunk starting at index {i}: {e}'))
                    raise e  # Raising the exception will trigger the atomic transaction rollback

                time.sleep(5)  # Sleep for 5 seconds before the next chunk