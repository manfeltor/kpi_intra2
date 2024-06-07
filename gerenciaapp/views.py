from django.shortcuts import render
import pandas as pd
import numpy as np
from entregasapp.models import bdoms, cpPais
from django.db.models import Q
import numpy as np
from .forms import DateRangeForm, DeliveryTypesForm
from .views_graph import interactive_bar_plot

# Create your views here.

def render_main_despacho_vs_entrega(request):
    if request.method == 'POST':
        form_dates = DateRangeForm(request.POST)
        form_filters = DeliveryTypesForm(request.POST)
        if form_dates.is_valid() and form_filters.is_valid():
            forms_data = fetch_entregas_forms_data(form_dates, form_filters)
            context = generate_main_despacho_vs_entrega_context(from_date_form=forms_data["from_date"], until_date_form=forms_data["to_date"], zona=forms_data["zona"])
            context['form'] = form_dates

            return render(request, "entregasmain.html", context)
    else:
        dates_form = DateRangeForm()
        delivery_form = DeliveryTypesForm()

    return render(request, "entregasmain.html", {'dates_form': dates_form, 'delivery_form' : delivery_form})

def generate_main_despacho_vs_entrega_context(from_date_form, until_date_form, zona):

    base_df = calculate_date_diff(first_date_column="fechaDespacho", last_date_column="fechaEntrega", zona=zona, tipo="DIST", from_date_filter=from_date_form, until_date_filter=until_date_form)

    mode_table = mode_group_date_diff(base_df, "codigoPostal__Provincia", "date_difference", "bdDate_difference")
    html_mode_table = mode_table.to_html(index=False)
    mode_graph = interactive_bar_plot(df=mode_table, x_column='codigoPostal__Provincia', y_column1='bdDate_difference', y_column2='date_difference', graph_title='graph_moda')

    mean_table = mean_group_date_diff(base_df, "codigoPostal__Provincia", "date_difference", "bdDate_difference")
    html_mean_table = mean_table.to_html(index=False)
    mean_graph = interactive_bar_plot(df=mean_table, x_column='codigoPostal__Provincia', y_column1='bdDate_difference', y_column2='date_difference', graph_title='graph_media')

    context = {'mode_table': html_mode_table, 'mode_graph': mode_graph, 'mean_table': html_mean_table, 'mean_graph': mean_graph}
    return context

def fetch_entregas_forms_data(form_dates, form_filters):
    
    from_date_form = form_dates.cleaned_data['start_date']
    until_date_form = form_dates.cleaned_data['end_date']
    # Extracting the values of AMBA and INTERIOR checkboxes
    amba_checked = form_filters.cleaned_data['AMBA']
    interior_checked = form_filters.cleaned_data['INTERIOR']
    # Determine the values for amba_filter and interior_filter based on checkbox values
    if amba_checked and not interior_checked: 
        
        zona_filter = "AMBA"

    elif not amba_checked and interior_checked:

        zona_filter = "INTERIOR"

    else:

        zona_filter = None

    cleaned_data = {"from_date":from_date_form, "to_date":until_date_form, "zona": zona_filter}

    return cleaned_data


#db

import pandas as pd

def calculate_days_between_first_and_last_reception(pedcol, datecol):

    df = bdoms.objects.filter()
    # Filter purchases with more than one piece
    multi_piece_purchases = df.groupby(pedcol).filter(lambda x: len(x) > 1)
    
    # Group the data by purchase number
    grouped = multi_piece_purchases.groupby(pedcol)
    
    # Initialize lists to store results
    results = []
    mono_piece_purchases = []
    
    # Iterate over each group
    for purchase_number, group_df in grouped:
        # Sort the group by reception date
        sorted_group = group_df.sort_values(by=datecol)
        
        # Get the first and last reception dates
        first_reception_date = sorted_group.iloc[0][datecol]
        last_reception_date = sorted_group.iloc[-1][datecol]
        
        # Calculate the date difference in days
        date_difference = (last_reception_date - first_reception_date).days
        
        # Append the result to the list
        results.append({'purchase_number': purchase_number, 'date_difference': date_difference})
    
    # Convert the list of results to a DataFrame
    result_df = pd.DataFrame(results)
    
    # Identify mono-piece purchases
    mono_piece_purchases = df[pedcol].unique()
    mono_piece_purchases = [p for p in mono_piece_purchases if p not in result_df[pedcol]]
    
    return result_df, len(mono_piece_purchases), len(results)


def calculate_date_diff(first_date_column, last_date_column, seller=None, zona=None, tipo=None, from_date_filter=None, until_date_filter=None):

        filter_conditions = Q()

        if seller:
            filter_conditions &= Q(seller=seller)
        if zona:
            filter_conditions &= Q(zona=zona)
        if tipo:
            filter_conditions &= Q(tipo=tipo)
        if from_date_filter and until_date_filter:
            filter_conditions &= Q(fechaDespacho__gte=from_date_filter, fechaDespacho__lte=until_date_filter)

        query_result = bdoms.objects.filter(filter_conditions).values(first_date_column, last_date_column, 'codigoPostal__Provincia')
        df = pd.DataFrame.from_records(query_result)
        df = df.dropna()
        df['date_difference'] = (df[last_date_column] - df[first_date_column]).dt.days
        A = [d.date() for d in df[first_date_column]]
        B = [d.date() for d in df[last_date_column]]
        df['bdDate_difference'] = np.busday_count(A, B)
        df = df[df['date_difference'] > 0]
        df = df[df['date_difference'] <= df['date_difference'].quantile(0.985)]
        
        return df

def bring_quartile(df, percentage, column):

    dffin = df[df[column] <= df[column].quantile(percentage)]

    return dffin

def mode_group_date_diff(df, grcol, datecol1, datecol2=None):
    if datecol2:
        mode_per_group = df.groupby(grcol)[[datecol1, datecol2]].apply(lambda x: x.mode())
    else:
        mode_per_group = df.groupby(grcol)[datecol1].apply(lambda x: x.mode())
    mode_per_group.reset_index(inplace=True)
    mode_per_group.drop(['level_1'], axis=1, inplace=True)
    # mode_per_group = mode_per_group[mode_per_group['codigoPostal__Provincia'] != 'CAPITAL FEDERAL']
    mode_per_group.sort_values(by=datecol1, inplace=True)
    return mode_per_group

def mean_group_date_diff(df, grcol, datecol1, datecol2=None):
    if datecol2:
        mean_per_group = df.groupby(grcol)[[datecol1, datecol2]].apply(lambda x: x.mean())
    else:
        mean_per_group = df.groupby(grcol)[datecol1].apply(lambda x: x.mean())
    mean_per_group.reset_index(inplace=True)

    # mean_per_group = mean_per_group[mean_per_group['codigoPostal__Provincia'] != 'CAPITAL FEDERAL']

    # Calculate first quartile for each group
    first_quartile = df.groupby(grcol)[datecol2].quantile(0.25).reset_index()
    first_quartile.rename(columns={datecol2: 'First_Quartile'}, inplace=True)

    second_quartile = df.groupby(grcol)[datecol2].quantile(0.50).reset_index()
    second_quartile.rename(columns={datecol2: 'Second_Quartile'}, inplace=True)

    third_quartile = df.groupby(grcol)[datecol2].quantile(0.75).reset_index()
    third_quartile.rename(columns={datecol2: 'third_quartile'}, inplace=True)

    last_quartile = df.groupby(grcol)[datecol2].quantile(0.95).reset_index()
    last_quartile.rename(columns={datecol2: '95_quartile'}, inplace=True)
    
    # Merge first quartile with mode_per_group DataFrame
    mean_per_group = mean_per_group.merge(first_quartile, on=grcol, how='left')
    mean_per_group = mean_per_group.merge(second_quartile, on=grcol, how='left')
    mean_per_group = mean_per_group.merge(third_quartile, on=grcol, how='left')
    mean_per_group = mean_per_group.merge(last_quartile, on=grcol, how='left')
    
    # Sort by datecol1
    mean_per_group.sort_values(by=datecol1, inplace=True)
    
    return mean_per_group

def importar_excel_tms(folder_path) -> pd.DataFrame:
    df = pd.read_excel(folder_path)
    df = df[[
    'pedido',
    'flujo',
    'seller',
    'sucCodigo',
    'estadoPedido',
    'fechaCreacion',
    'fechaRecepcion',
    'fechaDespacho',
    'fechaEntrega',
    'lpn',
    'estadoLpn',
    'trackingDistribucion',
    'trackingTransporte',
    'tipo',
    'codigoPostal',
    'tte',
    'tteSucursalDistribucion',
    'tiendaEntrega',
    'zona'
    ]]
    date_columns = ['fechaCreacion', 'fechaRecepcion', 'fechaDespacho', 'fechaEntrega']
    for column in date_columns:
        df[column] = pd.to_datetime(df[column])
    df['codigoPostal'] = df['codigoPostal'].astype(object)
    for index, row in df.iterrows():
        cp_value = row['codigoPostal']  # Assuming this is the CP value as a string
        cp_instance = cpPais.objects.get(CP=cp_value)
        df.at[index, 'codigoPostal'] = cp_instance
    bdfin = df
    for column in date_columns:
        print(column)
        bdfin[column] = pd.to_datetime(bdfin[column])
    bdfin.replace({pd.NaT: None, np.nan: None}, inplace=True)
    bdfin.replace('nan', None)
    # bdfin = bdfin.rename(columns=lambda x: x.replace('.', 'x'))
    # print(type(bdfin))
    return bdfin