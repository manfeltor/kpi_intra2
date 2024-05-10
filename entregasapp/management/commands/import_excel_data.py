from django.core.management.base import BaseCommand
from entregasapp.models import bdoms
from entregasapp.views import importar_excel_tms
from django.db import transaction

class Command(BaseCommand):
    help = 'Import data from Excel file into database'

    def handle(self, *args, **kwargs):
        # Full path to the Excel file - adjust as necessary
        excel_path = r'C:\Users\ftorres\OneDrive - INTRALOG ARGENTINA S.A\kpi\braw\mrgd\mrgd.xlsx'
        try:
            excel_data = importar_excel_tms(excel_path)
            total_rows = len(excel_data)
            objects_to_create = []
            batch_size = 1000  # You can adjust the batch size based on performance needs

            with transaction.atomic():  # One transaction for the entire process
                for index, row in excel_data.iterrows():
                    try:
                        obj = bdoms(**row.to_dict())
                        objects_to_create.append(obj)

                        # Check if it's time to flush the batch
                        if len(objects_to_create) >= batch_size or index == total_rows - 1:
                            bdoms.objects.bulk_create(objects_to_create)
                            objects_to_create = []  # Reset the batch

                            # Calculate and print progress
                            progress = (index + 1) / total_rows * 100
                            self.stdout.write(f"Progress: {progress:.2f}%")

                    except Exception as e:
                        # Log the error and problematic data, but continue processing
                        self.stdout.write(self.style.ERROR(f"Error preparing row {index + 1} for insertion: {e}"))
                        self.stdout.write(self.style.ERROR(f"Problematic data: {row}"))

                # This check is redundant because the last batch is handled in the loop
                # if objects_to_create:
                #     bdoms.objects.bulk_create(objects_to_create)

                self.stdout.write(self.style.SUCCESS('Data imported successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to import data: {e}'))