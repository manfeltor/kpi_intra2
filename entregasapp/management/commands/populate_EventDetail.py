import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from entregasapp.models import TrackingEventCA, EventDetail

class Command(BaseCommand):
    help = 'Populate EventDetail from TrackingEventCA raw data'

    def handle(self, *args, **kwargs):
        tracking_events = TrackingEventCA.objects.all()
        total_events = tracking_events.count()
        processed_events = 0
        
        for tracking_event in tracking_events:
            raw_data_str = tracking_event.raw_data
            raw_data = json.loads(raw_data_str)
            events = raw_data.get('event', [])

            with transaction.atomic():
                for event in events:
                    facility_code = event.get('facilityCode', 'UNKNOWN')
                    status_id = event.get('statusId', 'UNKNOWN')
                    status = event.get('status', 'UNKNOWN')
                    date_str = event.get('date', '01-01-1970 00:00:00')  # Default to Unix epoch if date is missing
                    sign = event.get('sign', '')
                    facility = event.get('facility', '')

                    try:
                        date = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
                    except ValueError:
                        date = datetime.strptime('01-01-1970 00:00', '%d-%m-%Y %H:%M')

                    try:
                        event_detail = EventDetail(
                            tracking_event=tracking_event,
                            facility_code=facility_code,
                            status_id=status_id,
                            status=status,
                            date=date,
                            sign=sign,
                            facility=facility
                        )
                        event_detail.save()
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to save event detail for {tracking_event.tracking_number}: {str(e)}"))

            processed_events += 1
            if processed_events % 100 == 0:
                self.stdout.write(self.style.SUCCESS(f"Processed {processed_events}/{total_events} tracking events"))

        self.stdout.write(self.style.SUCCESS('Successfully populated EventDetail from TrackingEventCA raw data'))