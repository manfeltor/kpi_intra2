import plotly.graph_objs as go
import pandas as pd

def interactive_bar_plot(df, x_column, y_column1, graph_title, y_column2 = None):
    # TODO test the func hard coded, then start passing DF
    
    # Specify the x and y values for the traces
    df_sorted = df.sort_values(by=y_column1)
    traces = []

    x_values = df_sorted[x_column]
    y_values1 = df_sorted[y_column1]
    trace1 = go.Bar(x=x_values, y=y_values1, name='y_column1', marker=dict(color='rgba(255,196,81, 0.8)'), width=0.3, offset=-0.15)
    traces.append(trace1)

    if y_column2:

        y_values2 = df_sorted[y_column2]
        trace2 = go.Bar(x=x_values, y=y_values2, name='y_column2', marker=dict(color='rgba(180,180,180, 0.8)'), width=0.3, offset=0.15)
        traces.append(trace2)

    # Create the Plotly figure
    fig = go.Figure(data=traces)
    fig.update_layout(title=graph_title, xaxis_title='X Axis Label', yaxis_title='Y Axis Label', plot_bgcolor='rgba(0,0,0, 0.8)')

    # Convert the figure to JSON
    graph_json = fig.to_json()

    return graph_json