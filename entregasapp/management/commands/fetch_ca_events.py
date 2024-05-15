import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models.functions import Length
from entregasapp.models import bdoms, TrackingEventCA
import requests
import time
import json

class Command(BaseCommand):
    help = 'Fetch and store tracking data for bdoms'

    def handle(self, *args, **options):
        api_key = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxOTEyNSIsIkNMQUlNX1RPS0VOIjoiUEVSTUlTU0lPTl9ERUZBVUxUIiwiaWF0IjoxNjkzMzMzNzM4LCJpc3MiOiJJU1NVRVIifQ.H2G4xWGgpESFMGO06YNYy_0l3tSw3ylmphZW4_y6ifU"
        agreement = "19125"
        url = "https://api.correoargentino.com.ar/paqar/v1/tracking"

        # Fetch distinct tracking numbers
        tracking_numbers = bdoms.objects.exclude(trackingTransporte__isnull=True)\
                                        .exclude(trackingTransporte__exact='')\
                                        .annotate(tracking_length=Length('trackingTransporte'))\
                                        .filter(tracking_length=18)\
                                        .values_list('trackingTransporte', flat=True)\
                                        .distinct()
        tracking_numbers = list(tracking_numbers)

        # Process in chunks of 20
        for i in range(0, len(tracking_numbers), 20):
            chunk = tracking_numbers[i:i+20]
            params = {"extClient": "", "trackingNumbers": chunk}
            headers = {"Authorization": f"Apikey {api_key}", "agreement": agreement}
            session = requests.Session()

            success = False
            attempts = 0
            while not success and attempts < 3:
                try:
                    response = session.get(url, headers=headers, params=params)
                    if response.status_code == 200:
                        data = json.loads(response.text)
                        for tracking_number, info in zip(chunk, data):
                            TrackingEventCA.objects.update_or_create(
                                tracking_number=tracking_number,
                                defaults={'data': info}
                            )
                        self.stdout.write(self.style.SUCCESS(f'Successfully processed chunk starting at index {i}'))
                        time.sleep(2)
                        success = True
                    else:
                        self.stdout.write(self.style.ERROR(f'API request failed for chunk starting at index {i}: {response.status_code} - {response.text}'))
                        attempts += 1
                        time.sleep(10)  # Sleep and retry
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing chunk starting at index {i}: {e}'))
                    attempts += 1
                    time.sleep(10)

            if not success:
                # Save failed chunk data to an Excel file
                self.save_failed_chunk_to_excel(chunk, i)
            
            if i % 100 == 0:  # Optionally clear the Django query cache every 100 chunks
                from django.db import connection
                connection.close()

    def save_failed_chunk_to_excel(self, chunk, index):
        # Query bdoms for the failed chunk
        failed_data = bdoms.objects.filter(trackingTransporte__in=chunk).values('pedido', 'trackingTransporte')
        df = pd.DataFrame(list(failed_data))
        filename = f'failed_chunk_starting_at_index_{index}.xlsx'
        df.to_excel(filename, index=False)
        self.stdout.write(self.style.ERROR(f'Saved failed chunk data to {filename}'))