import pandas as pd
import glob

pd.set_option('display.max_rows', None)
excel_data = r'C:\Users\ftorres\OneDrive - INTRALOG ARGENTINA S.A\kpi\dash_pr\TMS_por_meses\*.xlsx'

excel_files = glob.glob(excel_data)
df_inc = []
for file in excel_files:
    df = pd.read_excel(file)
    df_inc.append(df)

bdfin = pd.concat(df_inc, ignore_index=True)


date_columns = ['fechaCreacion', 'fechaColecta', 'fechaRecepcion', 'fechaDespacho', 'fechaEntrega']

for column in date_columns:
    bdfin[column] = bdfin[column].str[:10]

try:
    
    for i in date_columns:
        print(i)
        bdfin[i] = pd.to_datetime(bdfin[i])
        print(i, 'x')

except:

    pass
    
    # bdfin[date_columns] = pd.to_datetime(bdfin[date_columns], errors='coerce', format=r'%Y/%m/%d', utc=True)

# except ValueError as e:
#     print(f"Error: {e}")
#     print("The value that raised the error:")
    
#     # Find the problematic rows where the error occurred
#     problematic_rows = bdfin[date_columns].stack().loc[lambda x: pd.to_datetime(x, errors='coerce', utc=True).isna()]
    
#     # Print the entire row for each problematic row
#     for index, value in problematic_rows.items():
#         print(f"Problematic Row Index: {index}")
#         print(bdfin.loc[index])

# # print(type(bdfin))
# # print(bdfin.columns)
# # print(bdfin.dtypes)

