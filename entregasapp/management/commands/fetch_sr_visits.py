import time
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta, date
import requests
import json
from entregasapp.models import srVisit
# just to test
class Command(BaseCommand):
    help = 'Fetch and store visit data from API for each day since 2022-01-01'

    def handle(self, *args, **options):
        start_date = date(2022, 1, 1)
        end_date = now().date()
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            url = f"https://api.simpliroute.com/v1/routes/visits/?planned_date={date_str}"
            headers = {
                "authorization": "Token ac5e6e3f3e1afbf969e526b79f6227ee35b38801",
                "content-type": "application/json"
            }

            success = False
            attempts = 0

            while not success and attempts < 3:
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        data = json.loads(response.text)
                        srVisit.objects.update_or_create(date=current_date, defaults={'data': data})
                        self.stdout.write(self.style.SUCCESS(f'Successfully saved data for {date_str}'))
                        success = True
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to retrieve data for {date_str}: {response.status_code}'))
                        attempts += 1
                        time.sleep(2 ** attempts)  # Exponential backoff
                except requests.exceptions.RequestException as e:
                    self.stdout.write(self.style.ERROR(f'Request error on {date_str}: {e}'))
                    attempts += 1
                    time.sleep(2 ** attempts)  # Exponential backoff

            current_date += timedelta(days=1)
            time.sleep(1)