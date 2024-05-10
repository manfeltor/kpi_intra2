from entregasapp.models import bdoms

model_field_names = [field.name for field in bdoms._meta.get_fields()]

print(model_field_names)

# print(importar_excel_tms(r'C:\Users\ftorres\OneDrive - INTRALOG ARGENTINA S.A\kpi\dash_pr\TMS_por_meses\*.xlsx').columns)