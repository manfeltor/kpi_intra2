import pandas as pd
from django.core.management.base import BaseCommand
from entregasapp.models import cpPais

class Command(BaseCommand):
    help = 'Import data from Excel file into database'

    def handle(self, *args, **kwargs):
        
        excel_data = pd.read_excel('CP_tot.xlsx')

        for index, row in excel_data.iterrows():
            try:
                cpPais.objects.create(**row.to_dict())
            except Exception as e:
                print(f"Error inserting row {index + 1}: {e}")
                print(f"Problematic data: {row}")
                
        self.stdout.write(self.style.SUCCESS('Data imported successfully.'))
